"""
api/tasks.py

IMPORTANT: This project intentionally does NOT use Celery/Redis to keep the
stack simple. These are plain, synchronous Python functions containing the
"batch" business logic (coupon payouts, auto-reinvestment, maturity checks,
tax statement generation, notifications).

They can be invoked in three ways:
  1. On demand, via the Ops-only endpoints in views.py
     (RunCouponBatchView, RunReinvestmentBatchView).
  2. From the Django admin as an admin action.
  3. On a schedule, by wiring a Django management command
     (see management/commands/run_daily_batch.py) to system cron / a
     platform scheduler (e.g. `0 1 * * * python manage.py run_daily_batch`).

If the platform later needs true async/distributed processing, these
functions can be dropped into Celery tasks with zero change to their
internal logic — just wrap each with `@shared_task`.
"""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from . import models


# ----------------------------------------------------------------------
# Coupon payments
# ----------------------------------------------------------------------

def process_coupon_payments(as_of_date=None):
    """
    Finds coupon schedules due today (or `as_of_date`), creates
    CouponPayment records for every active Investment in that security,
    credits investor wallets (unless auto_reinvest is on), and sends a
    notification.
    """
    as_of_date = as_of_date or timezone.now().date()
    due_schedules = models.CouponSchedule.objects.filter(payment_date=as_of_date)

    paid_count = 0
    reinvested_count = 0
    total_paid = Decimal("0.00")

    for schedule in due_schedules:
        investments = models.Investment.objects.filter(
            security=schedule.security, status=models.Investment.Status.ACTIVE
        )
        for investment in investments:
            coupon_amount = (investment.amount_invested * schedule.rate / Decimal("100"))

            with transaction.atomic():
                coupon = models.CouponPayment.objects.create(
                    investment=investment, schedule=schedule,
                    amount=coupon_amount, payment_date=as_of_date,
                )

                if investment.auto_reinvest:
                    coupon.status = models.CouponPayment.Status.REINVESTED
                    coupon.paid_at = timezone.now()
                    coupon.save(update_fields=["status", "paid_at"])
                    reinvested_count += 1
                    # actual reinvestment purchase happens in run_auto_reinvestment()
                else:
                    wallet = investment.investor.wallet
                    wallet.credit(coupon_amount, models.WalletTransaction.TxType.COUPON,
                                  reference=f"coupon:{schedule.security.isin}")
                    coupon.status = models.CouponPayment.Status.PAID
                    coupon.paid_at = timezone.now()
                    coupon.save(update_fields=["status", "paid_at"])
                    paid_count += 1

                total_paid += coupon_amount

                models.Notification.objects.create(
                    user=investment.investor.user, channel=models.Notification.Channel.EMAIL,
                    title="Coupon Payment Processed",
                    message=f"You received a coupon payment of {coupon_amount} on {schedule.security.name}.",
                )

    return {
        "date": str(as_of_date),
        "securities_processed": due_schedules.count(),
        "coupons_paid": paid_count,
        "coupons_marked_for_reinvestment": reinvested_count,
        "total_amount": str(total_paid),
    }


# ----------------------------------------------------------------------
# Auto-reinvestment
# ----------------------------------------------------------------------

def run_auto_reinvestment():
    """
    Takes any CouponPayment marked REINVESTED that hasn't yet been rolled
    into a new Investment, and buys units of the best-available open
    security matching the investor's ReinvestmentRule preference.
    """
    pending = models.CouponPayment.objects.filter(
        status=models.CouponPayment.Status.REINVESTED
    ).select_related("investment__investor", "investment__security")

    reinvested_count = 0
    skipped_count = 0

    for coupon in pending:
        investor = coupon.investment.investor
        rule = models.ReinvestmentRule.objects.filter(investor=investor, is_active=True).first()

        if not rule or coupon.amount < rule.minimum_amount_threshold:
            skipped_count += 1
            continue

        preferred_type = rule.preferred_instrument_type or coupon.investment.security.instrument_type
        target_security = models.Security.objects.filter(
            instrument_type=preferred_type, status=models.Security.Status.OPEN,
        ).order_by("-coupon_rate").first()

        if not target_security:
            skipped_count += 1
            continue

        units = int(coupon.amount // target_security.face_value)
        if units < 1 or units > target_security.units_remaining:
            skipped_count += 1
            continue

        amount = target_security.face_value * units

        with transaction.atomic():
            order = models.Order.objects.create(
                investor=investor, security=target_security, order_type=models.Order.OrderType.BUY,
                units=units, amount=amount, status=models.Order.Status.EXECUTED, executed_at=timezone.now(),
            )
            models.Investment.objects.create(
                investor=investor, security=target_security, order=order,
                units=units, amount_invested=amount, auto_reinvest=True,
            )
            target_security.units_sold += units
            target_security.save(update_fields=["units_sold"])

        reinvested_count += 1
        models.Notification.objects.create(
            user=investor.user, channel=models.Notification.Channel.EMAIL,
            title="Coupon Reinvested",
            message=f"Your coupon of {coupon.amount} was reinvested into {target_security.name}.",
        )

    return {"reinvested": reinvested_count, "skipped": skipped_count}


# ----------------------------------------------------------------------
# Maturity handling
# ----------------------------------------------------------------------

def check_maturing_investments(as_of_date=None):
    """
    Marks investments as MATURED on their security's maturity date and
    credits face value + final coupon back to the investor wallet.
    """
    as_of_date = as_of_date or timezone.now().date()
    maturing = models.Investment.objects.filter(
        status=models.Investment.Status.ACTIVE, security__maturity_date=as_of_date,
    )

    matured_count = 0
    for investment in maturing:
        with transaction.atomic():
            wallet = investment.investor.wallet
            wallet.credit(
                investment.amount_invested, models.WalletTransaction.TxType.COUPON,
                reference=f"maturity:{investment.security.isin}",
            )
            investment.status = models.Investment.Status.MATURED
            investment.save(update_fields=["status"])

        matured_count += 1
        models.Notification.objects.create(
            user=investment.investor.user, channel=models.Notification.Channel.PUSH,
            title="Investment Matured",
            message=f"Your investment in {investment.security.name} has matured and been credited to your wallet.",
        )

    return {"date": str(as_of_date), "matured": matured_count}


# ----------------------------------------------------------------------
# Tax statements
# ----------------------------------------------------------------------

def generate_tax_statement(investor: models.InvestorProfile, tax_year: int) -> models.TaxStatement:
    """
    Aggregates coupon income for a calendar year into a TaxStatement
    record. PDF file generation is left as an integration point (e.g.
    WeasyPrint/ReportLab) — this function focuses on the data layer.
    """
    coupons = models.CouponPayment.objects.filter(
        investment__investor=investor,
        payment_date__year=tax_year,
        status__in=[models.CouponPayment.Status.PAID, models.CouponPayment.Status.REINVESTED],
    )
    total_interest = sum((c.amount for c in coupons), Decimal("0.00"))
    withholding_tax = total_interest * Decimal("0.15")  # example flat WHT rate, configurable

    statement, _ = models.TaxStatement.objects.update_or_create(
        investor=investor, tax_year=tax_year,
        defaults={
            "total_interest_earned": total_interest,
            "withholding_tax_paid": withholding_tax,
        },
    )
    return statement


# ----------------------------------------------------------------------
# Convenience: run everything in sequence (used by the daily cron command)
# ----------------------------------------------------------------------

def run_daily_batch():
    results = {
        "coupons": process_coupon_payments(),
        "reinvestment": run_auto_reinvestment(),
        "maturities": check_maturing_investments(),
    }
    return results