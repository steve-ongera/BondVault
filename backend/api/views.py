"""
api/views.py
All ViewSets / APIViews for BondVault, grouped to mirror models.py sections.
No Celery — background-style operations (coupons, reinvestment, tax
statements) live in tasks.py as plain functions triggered by Ops via an
endpoint or a simple cron-driven management command.
"""

from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions as drf_permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, permissions, serializers, tasks


def log_action(request, action_name, model_name="", object_id="", changes=None):
    models.AuditLog.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action=action_name,
        model_name=model_name,
        object_id=str(object_id),
        changes=changes or {},
        ip_address=request.META.get("REMOTE_ADDR"),
    )


def get_investor_profile(user):
    return get_object_or_404(models.InvestorProfile, user=user)


# ======================================================================
# 1. AUTH & KYC
# ======================================================================

class RegisterView(generics.CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.RegisterSerializer
    permission_classes = [drf_permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        log_action(request, "USER_REGISTERED", "User", response.data.get("id", ""))
        return response


class MeView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated]

    def get(self, request):
        return Response(serializers.UserSerializer(request.user).data)


class InvestorProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.InvestorProfileSerializer
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsOwnerInvestor]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.InvestorProfile.objects.all()
        if user.role == models.User.Role.ADVISOR:
            return models.InvestorProfile.objects.filter(advisor=user)
        return models.InvestorProfile.objects.filter(user=user)


class RiskProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.RiskProfileSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN, models.User.Role.ADVISOR):
            return models.RiskProfile.objects.all()
        return models.RiskProfile.objects.filter(investor__user=user)

    def perform_create(self, serializer):
        investor = get_investor_profile(self.request.user)
        serializer.save(investor=investor)


class KYCDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.KYCDocumentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.KYCDocument.objects.all()
        return models.KYCDocument.objects.filter(investor__user=user)

    def perform_create(self, serializer):
        investor = get_investor_profile(self.request.user)
        serializer.save(investor=investor)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsOpsOrAdmin])
    def review(self, request, pk=None):
        """Ops/Admin approves or rejects a single KYC document."""
        doc = self.get_object()
        serializer = serializers.KYCReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        doc.reviewed_by = request.user
        doc.reviewed_at = timezone.now()
        if serializer.validated_data["approve"]:
            doc.status = models.KYCDocument.Status.APPROVED
        else:
            doc.status = models.KYCDocument.Status.REJECTED
            doc.rejection_reason = serializer.validated_data.get("rejection_reason", "")
        doc.save()

        # If all required docs approved, mark investor's user as KYC verified
        investor = doc.investor
        if not investor.kyc_documents.exclude(status=models.KYCDocument.Status.APPROVED).exists():
            investor.user.is_kyc_verified = True
            investor.user.save(update_fields=["is_kyc_verified"])

        log_action(request, "KYC_REVIEWED", "KYCDocument", doc.id, {"status": doc.status})
        return Response(serializers.KYCDocumentSerializer(doc).data)


# ======================================================================
# 2. ACCOUNTS & MONEY
# ======================================================================

class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BankAccountSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.BankAccount.objects.all()
        return models.BankAccount.objects.filter(investor__user=user)

    def perform_create(self, serializer):
        serializer.save(investor=get_investor_profile(self.request.user))


class MobileMoneyAccountViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MobileMoneyAccountSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.MobileMoneyAccount.objects.all()
        return models.MobileMoneyAccount.objects.filter(investor__user=user)

    def perform_create(self, serializer):
        serializer.save(investor=get_investor_profile(self.request.user))


class WalletView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsInvestor]

    def get(self, request):
        investor = get_investor_profile(request.user)
        wallet, _ = models.Wallet.objects.get_or_create(investor=investor)
        return Response(serializers.WalletSerializer(wallet).data)


class WalletDepositView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsInvestor]

    def post(self, request):
        serializer = serializers.WalletFundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investor = get_investor_profile(request.user)
        wallet, _ = models.Wallet.objects.get_or_create(investor=investor)

        # NOTE: In production this triggers a real bank/mobile-money charge
        # request and only credits on a confirmed webhook callback.
        tx = wallet.credit(
            amount=serializer.validated_data["amount"],
            tx_type=models.WalletTransaction.TxType.DEPOSIT,
            reference=serializer.validated_data.get("reference", ""),
        )
        log_action(request, "WALLET_DEPOSIT", "WalletTransaction", tx.id)
        return Response(serializers.WalletTransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


class WalletWithdrawView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsInvestor]

    def post(self, request):
        serializer = serializers.WalletFundSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investor = get_investor_profile(request.user)
        wallet = get_object_or_404(models.Wallet, investor=investor)

        try:
            tx = wallet.debit(
                amount=serializer.validated_data["amount"],
                tx_type=models.WalletTransaction.TxType.WITHDRAWAL,
                reference=serializer.validated_data.get("reference", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        log_action(request, "WALLET_WITHDRAWAL", "WalletTransaction", tx.id)
        return Response(serializers.WalletTransactionSerializer(tx).data, status=status.HTTP_201_CREATED)


# ======================================================================
# 3. MARKETPLACE (Bonds & Treasury Bills)
# ======================================================================

class SecurityViewSet(viewsets.ModelViewSet):
    """Powers both the Bond Marketplace and the Treasury Bills Marketplace
    (frontend filters by ?instrument_type=BOND or TBILL)."""
    queryset = models.Security.objects.all().order_by("-issue_date")
    serializer_class = serializers.SecuritySerializer
    permission_classes = [permissions.ReadOnlyOrIsOpsAdmin]
    filterset_fields = ["instrument_type", "status"]

    def get_queryset(self):
        qs = super().get_queryset()
        instrument_type = self.request.query_params.get("instrument_type")
        status_param = self.request.query_params.get("status")
        if instrument_type:
            qs = qs.filter(instrument_type=instrument_type)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs


class BondAuctionViewSet(viewsets.ModelViewSet):
    queryset = models.BondAuction.objects.all().order_by("-auction_date")
    serializer_class = serializers.BondAuctionSerializer
    permission_classes = [permissions.ReadOnlyOrIsOpsAdmin]


# ======================================================================
# 4. INVESTING
# ======================================================================

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.OrderSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.Order.objects.all()
        return models.Order.objects.filter(investor__user=user)


class InvestmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.InvestmentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.Investment.objects.all()
        if user.role == models.User.Role.ADVISOR:
            return models.Investment.objects.filter(investor__advisor=user)
        return models.Investment.objects.filter(investor__user=user)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsInvestor, permissions.IsKYCVerified])
    def buy(self, request):
        """Purchase units of a Security, debiting the investor's wallet."""
        serializer = serializers.InvestmentPurchaseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        security = serializer.validated_data["security"]
        units = serializer.validated_data["units"]
        amount = security.face_value * units

        investor = get_investor_profile(request.user)
        wallet = get_object_or_404(models.Wallet, investor=investor)

        if amount < security.min_investment:
            return Response({"detail": "Amount below minimum investment"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                wallet.debit(amount, models.WalletTransaction.TxType.INVESTMENT, reference=security.isin)
            except ValueError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

            order = models.Order.objects.create(
                investor=investor, security=security, order_type=models.Order.OrderType.BUY,
                units=units, amount=amount, status=models.Order.Status.EXECUTED, executed_at=timezone.now(),
            )
            investment = models.Investment.objects.create(
                investor=investor, security=security, order=order,
                units=units, amount_invested=amount,
            )
            security.units_sold += units
            security.save(update_fields=["units_sold"])

        log_action(request, "INVESTMENT_PURCHASED", "Investment", investment.id, {"units": units, "amount": str(amount)})
        return Response(serializers.InvestmentSerializer(investment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsInvestor])
    def toggle_auto_reinvest(self, request, pk=None):
        investment = get_object_or_404(models.Investment, pk=pk, investor__user=request.user)
        investment.auto_reinvest = not investment.auto_reinvest
        investment.save(update_fields=["auto_reinvest"])
        return Response(serializers.InvestmentSerializer(investment).data)


# ======================================================================
# 5. SECONDARY MARKET
# ======================================================================

class SecondaryMarketListingViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SecondaryMarketListingSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            return models.SecondaryMarketListing.objects.filter(status=models.SecondaryMarketListing.Status.ACTIVE)
        return models.SecondaryMarketListing.objects.filter(seller__user=self.request.user)

    def perform_create(self, serializer):
        investor = get_investor_profile(self.request.user)
        investment = serializer.validated_data["investment"]
        if investment.investor_id != investor.id:
            raise generics.PermissionDenied("You do not own this investment.")
        serializer.save(seller=investor)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsInvestor, permissions.IsKYCVerified])
    def buy(self, request):
        """Execute a trade: buyer purchases units from an active listing."""
        serializer = serializers.TradeExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = get_object_or_404(
            models.SecondaryMarketListing, pk=serializer.validated_data["listing_id"],
            status=models.SecondaryMarketListing.Status.ACTIVE,
        )
        units = serializer.validated_data["units"]
        if units > listing.units_listed:
            return Response({"detail": "Not enough units in this listing"}, status=status.HTTP_400_BAD_REQUEST)

        buyer = get_investor_profile(request.user)
        total_amount = listing.price_per_unit * units
        buyer_wallet = get_object_or_404(models.Wallet, investor=buyer)
        seller_wallet = get_object_or_404(models.Wallet, investor=listing.seller)

        with transaction.atomic():
            try:
                buyer_wallet.debit(total_amount, models.WalletTransaction.TxType.TRADE_PURCHASE, reference=str(listing.id))
            except ValueError as exc:
                return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
            seller_wallet.credit(total_amount, models.WalletTransaction.TxType.TRADE_SALE, reference=str(listing.id))

            trade = models.Trade.objects.create(
                listing=listing, buyer=buyer, units=units,
                price_per_unit=listing.price_per_unit, total_amount=total_amount,
            )

            models.Investment.objects.create(
                investor=buyer, security=listing.investment.security,
                units=units, amount_invested=total_amount,
            )

            listing.units_listed -= units
            if listing.units_listed == 0:
                listing.status = models.SecondaryMarketListing.Status.SOLD
            listing.save()

        log_action(request, "SECONDARY_TRADE_EXECUTED", "Trade", trade.id)
        return Response(serializers.TradeSerializer(trade).data, status=status.HTTP_201_CREATED)


# ======================================================================
# 6. INCOME
# ======================================================================

class CouponPaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.CouponPaymentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.CouponPayment.objects.all()
        return models.CouponPayment.objects.filter(investment__investor__user=user)


class ReinvestmentRuleViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ReinvestmentRuleSerializer
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsInvestor]

    def get_queryset(self):
        return models.ReinvestmentRule.objects.filter(investor__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(investor=get_investor_profile(self.request.user))


class RunCouponBatchView(APIView):
    """Manually triggered by Ops (replaces a Celery beat schedule)."""
    permission_classes = [permissions.IsOpsOrAdmin]

    def post(self, request):
        result = tasks.process_coupon_payments()
        log_action(request, "COUPON_BATCH_RUN", changes=result)
        return Response(result)


class RunReinvestmentBatchView(APIView):
    permission_classes = [permissions.IsOpsOrAdmin]

    def post(self, request):
        result = tasks.run_auto_reinvestment()
        log_action(request, "REINVESTMENT_BATCH_RUN", changes=result)
        return Response(result)


# ======================================================================
# 7. DOCUMENTS
# ======================================================================

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DocumentSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.Document.objects.all()
        return models.Document.objects.filter(investor__user=user)

    def perform_create(self, serializer):
        serializer.save(investor=get_investor_profile(self.request.user))


class TaxStatementViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.TaxStatementSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (models.User.Role.OPS, models.User.Role.ADMIN):
            return models.TaxStatement.objects.all()
        return models.TaxStatement.objects.filter(investor__user=user)

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsInvestor])
    def generate(self, request):
        year = int(request.data.get("tax_year", timezone.now().year - 1))
        investor = get_investor_profile(request.user)
        statement = tasks.generate_tax_statement(investor, year)
        return Response(serializers.TaxStatementSerializer(statement).data, status=status.HTTP_201_CREATED)


# ======================================================================
# 8. GOVERNANCE
# ======================================================================

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.AuditLog.objects.all()
    serializer_class = serializers.AuditLogSerializer
    permission_classes = [permissions.IsSuperAdmin]


class ComplianceFlagViewSet(viewsets.ModelViewSet):
    queryset = models.ComplianceFlag.objects.all()
    serializer_class = serializers.ComplianceFlagSerializer
    permission_classes = [permissions.IsOpsOrAdmin]

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        flag = self.get_object()
        flag.status = models.ComplianceFlag.Status.RESOLVED
        flag.resolved_by = request.user
        flag.resolved_at = timezone.now()
        flag.save()
        return Response(serializers.ComplianceFlagSerializer(flag).data)


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.NotificationSerializer
    permission_classes = [drf_permissions.IsAuthenticated]

    def get_queryset(self):
        return models.Notification.objects.filter(user=self.request.user)

    @action(detail=True, methods=["patch"])
    def mark_read(self, request, pk=None):
        note = get_object_or_404(models.Notification, pk=pk, user=request.user)
        note.is_read = True
        note.save(update_fields=["is_read"])
        return Response(serializers.NotificationSerializer(note).data)


# ======================================================================
# 9. DASHBOARD & TOOLS
# ======================================================================

class DashboardView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsInvestor]

    def get(self, request):
        investor = get_investor_profile(request.user)
        investments = models.Investment.objects.filter(investor=investor, status=models.Investment.Status.ACTIVE)
        wallet, _ = models.Wallet.objects.get_or_create(investor=investor)

        total_portfolio_value = sum((inv.current_value for inv in investments), Decimal("0.00"))
        total_invested = sum((inv.amount_invested for inv in investments), Decimal("0.00"))
        total_interest_earned = total_portfolio_value - total_invested

        upcoming_coupons = models.CouponPayment.objects.filter(
            investment__investor=investor, status=models.CouponPayment.Status.PENDING
        ).order_by("payment_date")[:10]

        maturing = investments.filter(
            security__maturity_date__lte=timezone.now().date() + timezone.timedelta(days=30)
        )

        allocation = {}
        for inv in investments:
            key = inv.security.instrument_type
            allocation[key] = allocation.get(key, Decimal("0.00")) + inv.current_value

        monthly_income_projection = sum(
            (inv.amount_invested * (inv.security.coupon_rate / Decimal("100")) / Decimal("12") for inv in investments),
            Decimal("0.00"),
        )

        recent_tx = wallet.transactions.order_by("-created_at")[:10]

        data = {
            "total_portfolio_value": total_portfolio_value,
            "total_interest_earned": total_interest_earned,
            "wallet_balance": wallet.balance,
            "active_bonds_count": investments.count(),
            "upcoming_coupon_payments": upcoming_coupons,
            "maturing_investments": maturing,
            "asset_allocation": allocation,
            "monthly_income_projection": monthly_income_projection,
            "recent_transactions": recent_tx,
        }
        return Response(serializers.DashboardSummarySerializer(data).data)


class InvestmentCalculatorView(APIView):
    permission_classes = [drf_permissions.AllowAny]

    def post(self, request):
        serializer = serializers.InvestmentCalculatorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        principal = serializer.validated_data["principal"]
        annual_rate = serializer.validated_data["annual_rate"]
        tenor_days = serializer.validated_data["tenor_days"]

        interest = principal * (annual_rate / Decimal("100")) * (Decimal(tenor_days) / Decimal("365"))
        maturity_value = principal + interest
        effective_annual_yield = (interest / principal) * (Decimal("365") / Decimal(tenor_days)) * Decimal("100")

        result = {
            "principal": principal,
            "estimated_interest": round(interest, 2),
            "estimated_maturity_value": round(maturity_value, 2),
            "effective_annual_yield": round(effective_annual_yield, 3),
        }
        return Response(serializers.InvestmentCalculatorResultSerializer(result).data)


class AdvisorDashboardView(APIView):
    permission_classes = [drf_permissions.IsAuthenticated, permissions.IsAdvisor]

    def get(self, request):
        investors = models.InvestorProfile.objects.filter(advisor=request.user)
        return Response(serializers.InvestorProfileSerializer(investors, many=True).data)


class OpsKYCQueueView(APIView):
    permission_classes = [permissions.IsOpsOrAdmin]

    def get(self, request):
        pending = models.KYCDocument.objects.filter(status=models.KYCDocument.Status.PENDING)
        return Response(serializers.KYCDocumentSerializer(pending, many=True).data)