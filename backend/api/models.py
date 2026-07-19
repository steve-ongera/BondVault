"""
api/models.py
Single-app monolith model layer for BondVault.
Models are grouped into clearly commented sections so this file can later
be split into per-domain apps without changing field names or relations.
"""

import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# ======================================================================
# 1. IDENTITY & KYC
# ======================================================================

class User(AbstractUser):
    class Role(models.TextChoices):
        INVESTOR = "INVESTOR", "Investor"
        ADVISOR = "ADVISOR", "Investment Advisor"
        OPS = "OPS", "Operations Team"
        ADMIN = "ADMIN", "Super Administrator"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.INVESTOR)
    phone_number = models.CharField(max_length=20, blank=True)
    is_kyc_verified = models.BooleanField(default=False)
    is_active_investor = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="investor_profile")
    date_of_birth = models.DateField(null=True, blank=True)
    national_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    residential_address = models.TextField(blank=True)
    next_of_kin_name = models.CharField(max_length=150, blank=True)
    next_of_kin_phone = models.CharField(max_length=20, blank=True)
    advisor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="assigned_investors",
        limit_choices_to={"role": User.Role.ADVISOR},
    )
    occupation = models.CharField(max_length=150, blank=True)
    monthly_income_band = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class RiskProfile(models.Model):
    class Category(models.TextChoices):
        CONSERVATIVE = "CONSERVATIVE", "Conservative"
        MODERATE = "MODERATE", "Moderate"
        AGGRESSIVE = "AGGRESSIVE", "Aggressive"

    investor = models.OneToOneField(InvestorProfile, on_delete=models.CASCADE, related_name="risk_profile")
    score = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.MODERATE)
    answers = models.JSONField(default=dict, blank=True)
    assessed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.investor.user.username} - {self.category}"


class KYCDocument(models.Model):
    class DocType(models.TextChoices):
        NATIONAL_ID = "NATIONAL_ID", "National ID"
        PASSPORT = "PASSPORT", "Passport"
        PROOF_OF_ADDRESS = "PROOF_OF_ADDRESS", "Proof of Address"
        SELFIE = "SELFIE", "Selfie / Liveness"
        TAX_PIN = "TAX_PIN", "Tax PIN Certificate"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="kyc_documents")
    doc_type = models.CharField(max_length=30, choices=DocType.choices)
    file = models.FileField(upload_to="kyc_documents/%Y/%m/")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="kyc_reviews")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.investor.user.username} - {self.doc_type} - {self.status}"


# ======================================================================
# 2. ACCOUNTS & MONEY
# ======================================================================

class BankAccount(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="bank_accounts")
    bank_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=50)
    account_name = models.CharField(max_length=150)
    branch_code = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"


class MobileMoneyAccount(models.Model):
    class Provider(models.TextChoices):
        MPESA = "MPESA", "M-Pesa"
        AIRTEL_MONEY = "AIRTEL_MONEY", "Airtel Money"
        T_KASH = "T_KASH", "T-Kash"

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="mobile_money_accounts")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    phone_number = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.provider} - {self.phone_number}"


class Wallet(models.Model):
    investor = models.OneToOneField(InvestorProfile, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(max_length=10, default="KES")
    updated_at = models.DateTimeField(auto_now=True)

    def credit(self, amount: Decimal, tx_type: str, reference: str = "") -> "WalletTransaction":
        self.balance += amount
        self.save(update_fields=["balance", "updated_at"])
        return WalletTransaction.objects.create(
            wallet=self, tx_type=tx_type, amount=amount,
            balance_after=self.balance, reference=reference, status=WalletTransaction.Status.SUCCESS,
        )

    def debit(self, amount: Decimal, tx_type: str, reference: str = "") -> "WalletTransaction":
        if amount > self.balance:
            raise ValueError("Insufficient wallet balance")
        self.balance -= amount
        self.save(update_fields=["balance", "updated_at"])
        return WalletTransaction.objects.create(
            wallet=self, tx_type=tx_type, amount=-amount,
            balance_after=self.balance, reference=reference, status=WalletTransaction.Status.SUCCESS,
        )

    def __str__(self):
        return f"Wallet: {self.investor.user.username} - {self.balance} {self.currency}"


class WalletTransaction(models.Model):
    class TxType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Deposit"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        INVESTMENT = "INVESTMENT", "Investment Purchase"
        COUPON = "COUPON", "Coupon Payment"
        REINVESTMENT = "REINVESTMENT", "Reinvestment"
        TRADE_SALE = "TRADE_SALE", "Secondary Market Sale"
        TRADE_PURCHASE = "TRADE_PURCHASE", "Secondary Market Purchase"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    tx_type = models.CharField(max_length=20, choices=TxType.choices)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    balance_after = models.DecimalField(max_digits=18, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tx_type} - {self.amount} - {self.status}"


# ======================================================================
# 3. INSTRUMENTS (Bonds & Treasury Bills unified under one model)
# ======================================================================

class Security(models.Model):
    class InstrumentType(models.TextChoices):
        BOND = "BOND", "Government Bond"
        TBILL = "TBILL", "Treasury Bill"

    class Status(models.TextChoices):
        UPCOMING = "UPCOMING", "Upcoming"
        OPEN = "OPEN", "Open for Subscription"
        CLOSED = "CLOSED", "Subscription Closed"
        MATURED = "MATURED", "Matured"

    instrument_type = models.CharField(max_length=10, choices=InstrumentType.choices)
    name = models.CharField(max_length=150)
    isin = models.CharField(max_length=20, unique=True)
    issue_date = models.DateField()
    maturity_date = models.DateField()
    tenor_days = models.PositiveIntegerField(help_text="Tenor in days, e.g. 91, 182, 364, 1825")
    coupon_rate = models.DecimalField(max_digits=6, decimal_places=3, help_text="Annual coupon / yield rate, %")
    face_value = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("100.00"))
    min_investment = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("3000.00"))
    total_units_available = models.PositiveIntegerField()
    units_sold = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UPCOMING)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def units_remaining(self) -> int:
        return self.total_units_available - self.units_sold

    def __str__(self):
        return f"{self.name} ({self.instrument_type})"


class BondAuction(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "SCHEDULED", "Scheduled"
        OPEN = "OPEN", "Open"
        CLOSED = "CLOSED", "Closed"
        SETTLED = "SETTLED", "Settled"

    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name="auctions")
    auction_date = models.DateField()
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    clearing_rate = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.SCHEDULED)

    def __str__(self):
        return f"Auction: {self.security.name} - {self.auction_date}"


class CouponSchedule(models.Model):
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name="coupon_schedule")
    sequence = models.PositiveIntegerField()
    payment_date = models.DateField()
    rate = models.DecimalField(max_digits=6, decimal_places=3)

    class Meta:
        ordering = ["sequence"]
        unique_together = ("security", "sequence")

    def __str__(self):
        return f"{self.security.name} - coupon #{self.sequence} on {self.payment_date}"


# ======================================================================
# 4. INVESTING
# ======================================================================

class Order(models.Model):
    class OrderType(models.TextChoices):
        BUY = "BUY", "Buy"
        SELL = "SELL", "Sell"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        EXECUTED = "EXECUTED", "Executed"
        CANCELLED = "CANCELLED", "Cancelled"
        FAILED = "FAILED", "Failed"

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="orders")
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name="orders")
    order_type = models.CharField(max_length=10, choices=OrderType.choices)
    units = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_type} {self.units} units of {self.security.name}"


class Investment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        MATURED = "MATURED", "Matured"
        SOLD = "SOLD", "Sold on Secondary Market"

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="investments")
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name="investments")
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name="investment")
    units = models.PositiveIntegerField()
    amount_invested = models.DecimalField(max_digits=18, decimal_places=2)
    purchase_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    auto_reinvest = models.BooleanField(default=False)

    @property
    def current_value(self) -> Decimal:
        """Simplified accrued value = principal + accrued coupon since purchase."""
        days_held = (timezone.now().date() - self.purchase_date).days
        daily_rate = (self.security.coupon_rate / Decimal("100")) / Decimal("365")
        accrued = self.amount_invested * daily_rate * Decimal(days_held)
        return self.amount_invested + accrued

    def __str__(self):
        return f"{self.investor.user.username} - {self.security.name} - {self.units} units"


# ======================================================================
# 5. SECONDARY MARKET
# ======================================================================

class SecondaryMarketListing(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        SOLD = "SOLD", "Sold"
        CANCELLED = "CANCELLED", "Cancelled"

    seller = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="listings")
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name="listings")
    units_listed = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    listed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Listing: {self.investment.security.name} x{self.units_listed} @ {self.price_per_unit}"


class Trade(models.Model):
    listing = models.ForeignKey(SecondaryMarketListing, on_delete=models.CASCADE, related_name="trades")
    buyer = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="purchases")
    units = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=18, decimal_places=2)
    total_amount = models.DecimalField(max_digits=18, decimal_places=2)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trade: {self.buyer.user.username} bought {self.units} units"


# ======================================================================
# 6. INCOME (Coupons & Reinvestment)
# ======================================================================

class CouponPayment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        REINVESTED = "REINVESTED", "Reinvested"

    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name="coupon_payments")
    schedule = models.ForeignKey(CouponSchedule, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    payment_date = models.DateField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Coupon: {self.investment} - {self.amount} - {self.status}"


class ReinvestmentRule(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="reinvestment_rules")
    is_active = models.BooleanField(default=True)
    preferred_instrument_type = models.CharField(
        max_length=10, choices=Security.InstrumentType.choices, blank=True,
        help_text="Leave blank to reinvest into the same instrument type as the original investment",
    )
    minimum_amount_threshold = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("1000.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReinvestRule: {self.investor.user.username} - active={self.is_active}"


# ======================================================================
# 7. DOCUMENTS
# ======================================================================

class Document(models.Model):
    class DocType(models.TextChoices):
        CONTRACT_NOTE = "CONTRACT_NOTE", "Contract Note"
        STATEMENT = "STATEMENT", "Account Statement"
        CERTIFICATE = "CERTIFICATE", "Investment Certificate"
        OTHER = "OTHER", "Other"

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="documents")
    doc_type = models.CharField(max_length=20, choices=DocType.choices)
    file = models.FileField(upload_to="documents/%Y/%m/")
    title = models.CharField(max_length=150)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.investor.user.username}"


class TaxStatement(models.Model):
    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="tax_statements")
    tax_year = models.PositiveIntegerField()
    file = models.FileField(upload_to="tax_statements/%Y/")
    total_interest_earned = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    withholding_tax_paid = models.DecimalField(max_digits=18, decimal_places=2, default=Decimal("0.00"))
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("investor", "tax_year")

    def __str__(self):
        return f"TaxStatement: {self.investor.user.username} - {self.tax_year}"


# ======================================================================
# 8. GOVERNANCE (Audit, Compliance, Notifications)
# ======================================================================

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=100, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action}"


class ComplianceFlag(models.Model):
    class FlagType(models.TextChoices):
        LARGE_TRANSACTION = "LARGE_TRANSACTION", "Large / Unusual Transaction"
        PEP = "PEP", "Politically Exposed Person"
        DOCUMENT_MISMATCH = "DOCUMENT_MISMATCH", "Document Mismatch"
        VELOCITY = "VELOCITY", "Transaction Velocity Alert"
        OTHER = "OTHER", "Other"

    class Status(models.TextChoices):
        OPEN = "OPEN", "Open"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        RESOLVED = "RESOLVED", "Resolved"

    investor = models.ForeignKey(InvestorProfile, on_delete=models.CASCADE, related_name="compliance_flags")
    flag_type = models.CharField(max_length=25, choices=FlagType.choices)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="resolved_flags")
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.flag_type} - {self.investor.user.username} - {self.status}"


class Notification(models.Model):
    class Channel(models.TextChoices):
        SMS = "SMS", "SMS"
        EMAIL = "EMAIL", "Email"
        PUSH = "PUSH", "Push"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=10, choices=Channel.choices)
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.channel} to {self.user.username}: {self.title}"