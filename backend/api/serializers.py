"""
api/serializers.py
All DRF serializers for BondVault, grouped to mirror models.py sections.
"""

from decimal import Decimal

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from . import models


# ======================================================================
# 1. IDENTITY & KYC
# ======================================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["id", "username", "email", "first_name", "last_name",
                  "role", "phone_number", "is_kyc_verified", "created_at"]
        read_only_fields = ["id", "is_kyc_verified", "created_at"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = models.User
        fields = ["username", "email", "password", "first_name", "last_name", "phone_number"]

    def create(self, validated_data):
        user = models.User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            phone_number=validated_data.get("phone_number", ""),
            role=models.User.Role.INVESTOR,
        )
        investor_profile = models.InvestorProfile.objects.create(user=user)
        models.Wallet.objects.create(investor=investor_profile)
        return user


class InvestorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    advisor_name = serializers.CharField(source="advisor.get_full_name", read_only=True)

    class Meta:
        model = models.InvestorProfile
        fields = ["id", "user", "date_of_birth", "national_id", "residential_address",
                  "next_of_kin_name", "next_of_kin_phone", "advisor", "advisor_name",
                  "occupation", "monthly_income_band", "created_at"]
        read_only_fields = ["id", "created_at"]


class RiskProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RiskProfile
        fields = ["id", "investor", "score", "category", "answers", "assessed_at"]
        read_only_fields = ["id", "assessed_at"]


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KYCDocument
        fields = ["id", "investor", "doc_type", "file", "status",
                  "reviewed_by", "reviewed_at", "rejection_reason", "uploaded_at"]
        read_only_fields = ["id", "status", "reviewed_by", "reviewed_at", "uploaded_at"]


class KYCReviewSerializer(serializers.Serializer):
    """Used by Ops to approve/reject a KYC document."""
    approve = serializers.BooleanField()
    rejection_reason = serializers.CharField(required=False, allow_blank=True)


# ======================================================================
# 2. ACCOUNTS & MONEY
# ======================================================================

class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BankAccount
        fields = ["id", "investor", "bank_name", "account_number", "account_name",
                  "branch_code", "is_verified", "is_primary", "created_at"]
        read_only_fields = ["id", "investor", "is_verified", "created_at"]


class MobileMoneyAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MobileMoneyAccount
        fields = ["id", "investor", "provider", "phone_number",
                  "is_verified", "is_primary", "created_at"]
        read_only_fields = ["id", "investor", "is_verified", "created_at"]


class WalletTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WalletTransaction
        fields = ["id", "tx_type", "amount", "balance_after", "reference", "status", "created_at"]
        read_only_fields = fields


class WalletSerializer(serializers.ModelSerializer):
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = models.Wallet
        fields = ["id", "balance", "currency", "updated_at", "recent_transactions"]
        read_only_fields = fields

    def get_recent_transactions(self, obj):
        qs = obj.transactions.order_by("-created_at")[:10]
        return WalletTransactionSerializer(qs, many=True).data


class WalletFundSerializer(serializers.Serializer):
    """Used for deposit / withdrawal requests."""
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("1.00"))
    channel = serializers.ChoiceField(choices=["BANK", "MOBILE_MONEY"])
    reference = serializers.CharField(required=False, allow_blank=True)


# ======================================================================
# 3. INSTRUMENTS
# ======================================================================

class CouponScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CouponSchedule
        fields = ["id", "sequence", "payment_date", "rate"]


class SecuritySerializer(serializers.ModelSerializer):
    units_remaining = serializers.ReadOnlyField()
    coupon_schedule = CouponScheduleSerializer(many=True, read_only=True)

    class Meta:
        model = models.Security
        fields = ["id", "instrument_type", "name", "isin", "issue_date", "maturity_date",
                  "tenor_days", "coupon_rate", "face_value", "min_investment",
                  "total_units_available", "units_sold", "units_remaining",
                  "status", "description", "coupon_schedule", "created_at"]
        read_only_fields = ["id", "units_sold", "created_at"]


class BondAuctionSerializer(serializers.ModelSerializer):
    security_name = serializers.CharField(source="security.name", read_only=True)

    class Meta:
        model = models.BondAuction
        fields = ["id", "security", "security_name", "auction_date",
                  "opens_at", "closes_at", "clearing_rate", "status"]
        read_only_fields = ["id"]


# ======================================================================
# 4. INVESTING
# ======================================================================

class OrderSerializer(serializers.ModelSerializer):
    security_name = serializers.CharField(source="security.name", read_only=True)

    class Meta:
        model = models.Order
        fields = ["id", "investor", "security", "security_name", "order_type",
                  "units", "amount", "status", "created_at", "executed_at"]
        read_only_fields = ["id", "investor", "status", "created_at", "executed_at"]


class InvestmentSerializer(serializers.ModelSerializer):
    security = SecuritySerializer(read_only=True)
    current_value = serializers.ReadOnlyField()

    class Meta:
        model = models.Investment
        fields = ["id", "investor", "security", "units", "amount_invested",
                  "purchase_date", "status", "auto_reinvest", "current_value"]
        read_only_fields = ["id", "investor", "security", "units",
                             "amount_invested", "purchase_date", "status", "current_value"]


class InvestmentPurchaseSerializer(serializers.Serializer):
    """Used to place a BUY order against a security."""
    security_id = serializers.IntegerField()
    units = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        try:
            security = models.Security.objects.get(id=attrs["security_id"])
        except models.Security.DoesNotExist:
            raise serializers.ValidationError("Security not found")
        if security.status != models.Security.Status.OPEN:
            raise serializers.ValidationError("Security is not open for subscription")
        if attrs["units"] > security.units_remaining:
            raise serializers.ValidationError("Not enough units remaining")
        attrs["security"] = security
        return attrs


# ======================================================================
# 5. SECONDARY MARKET
# ======================================================================

class SecondaryMarketListingSerializer(serializers.ModelSerializer):
    security_name = serializers.CharField(source="investment.security.name", read_only=True)

    class Meta:
        model = models.SecondaryMarketListing
        fields = ["id", "seller", "investment", "security_name", "units_listed",
                  "price_per_unit", "status", "listed_at"]
        read_only_fields = ["id", "seller", "status", "listed_at"]


class TradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trade
        fields = ["id", "listing", "buyer", "units", "price_per_unit", "total_amount", "executed_at"]
        read_only_fields = fields


class TradeExecuteSerializer(serializers.Serializer):
    """Used by a buyer to purchase units from a listing."""
    listing_id = serializers.IntegerField()
    units = serializers.IntegerField(min_value=1)


# ======================================================================
# 6. INCOME
# ======================================================================

class CouponPaymentSerializer(serializers.ModelSerializer):
    security_name = serializers.CharField(source="investment.security.name", read_only=True)

    class Meta:
        model = models.CouponPayment
        fields = ["id", "investment", "security_name", "amount",
                  "payment_date", "status", "paid_at"]
        read_only_fields = fields


class ReinvestmentRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ReinvestmentRule
        fields = ["id", "investor", "is_active", "preferred_instrument_type",
                  "minimum_amount_threshold", "created_at"]
        read_only_fields = ["id", "investor", "created_at"]


# ======================================================================
# 7. DOCUMENTS
# ======================================================================

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = ["id", "investor", "doc_type", "file", "title", "uploaded_at"]
        read_only_fields = ["id", "investor", "uploaded_at"]


class TaxStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TaxStatement
        fields = ["id", "investor", "tax_year", "file", "total_interest_earned",
                  "withholding_tax_paid", "generated_at"]
        read_only_fields = fields


# ======================================================================
# 8. GOVERNANCE
# ======================================================================

class AuditLogSerializer(serializers.ModelSerializer):
    user_display = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = models.AuditLog
        fields = ["id", "user", "user_display", "action", "model_name",
                  "object_id", "changes", "ip_address", "timestamp"]
        read_only_fields = fields


class ComplianceFlagSerializer(serializers.ModelSerializer):
    investor_name = serializers.CharField(source="investor.user.username", read_only=True)

    class Meta:
        model = models.ComplianceFlag
        fields = ["id", "investor", "investor_name", "flag_type", "description",
                  "status", "resolved_by", "created_at", "resolved_at"]
        read_only_fields = ["id", "created_at", "resolved_at"]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Notification
        fields = ["id", "channel", "title", "message", "is_read", "created_at"]
        read_only_fields = ["id", "channel", "title", "message", "created_at"]


# ======================================================================
# 9. DASHBOARD / AGGREGATE (non-model serializers)
# ======================================================================

class DashboardSummarySerializer(serializers.Serializer):
    total_portfolio_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    total_interest_earned = serializers.DecimalField(max_digits=18, decimal_places=2)
    wallet_balance = serializers.DecimalField(max_digits=18, decimal_places=2)
    active_bonds_count = serializers.IntegerField()
    upcoming_coupon_payments = CouponPaymentSerializer(many=True)
    maturing_investments = InvestmentSerializer(many=True)
    asset_allocation = serializers.DictField()
    monthly_income_projection = serializers.DecimalField(max_digits=18, decimal_places=2)
    recent_transactions = WalletTransactionSerializer(many=True)


class InvestmentCalculatorSerializer(serializers.Serializer):
    principal = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("1.00"))
    annual_rate = serializers.DecimalField(max_digits=6, decimal_places=3)
    tenor_days = serializers.IntegerField(min_value=1)


class InvestmentCalculatorResultSerializer(serializers.Serializer):
    principal = serializers.DecimalField(max_digits=18, decimal_places=2)
    estimated_interest = serializers.DecimalField(max_digits=18, decimal_places=2)
    estimated_maturity_value = serializers.DecimalField(max_digits=18, decimal_places=2)
    effective_annual_yield = serializers.DecimalField(max_digits=6, decimal_places=3)