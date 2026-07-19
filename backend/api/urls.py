"""
api/urls.py
App-level URL configuration for BondVault's single `api` app.
Included into config/urls.py via: path("api/", include("api.urls"))
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

# ----------------------------------------------------------------------
# Router-registered ViewSets
# ----------------------------------------------------------------------
router = DefaultRouter()
router.register(r"investor-profiles", views.InvestorProfileViewSet, basename="investor-profile")
router.register(r"risk-profiles", views.RiskProfileViewSet, basename="risk-profile")
router.register(r"kyc-documents", views.KYCDocumentViewSet, basename="kyc-document")
router.register(r"bank-accounts", views.BankAccountViewSet, basename="bank-account")
router.register(r"mobile-money-accounts", views.MobileMoneyAccountViewSet, basename="mobile-money-account")
router.register(r"securities", views.SecurityViewSet, basename="security")
router.register(r"auctions", views.BondAuctionViewSet, basename="auction")
router.register(r"orders", views.OrderViewSet, basename="order")
router.register(r"investments", views.InvestmentViewSet, basename="investment")
router.register(r"secondary-market/listings", views.SecondaryMarketListingViewSet, basename="secondary-listing")
router.register(r"coupons", views.CouponPaymentViewSet, basename="coupon")
router.register(r"reinvestment-rules", views.ReinvestmentRuleViewSet, basename="reinvestment-rule")
router.register(r"documents", views.DocumentViewSet, basename="document")
router.register(r"tax-statements", views.TaxStatementViewSet, basename="tax-statement")
router.register(r"audit-logs", views.AuditLogViewSet, basename="audit-log")
router.register(r"compliance-flags", views.ComplianceFlagViewSet, basename="compliance-flag")
router.register(r"notifications", views.NotificationViewSet, basename="notification")

urlpatterns = [
    # ---- Auth ----
    path("auth/register/", views.RegisterView.as_view(), name="auth-register"),
    path("auth/login/", TokenObtainPairView.as_view(), name="auth-login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="auth-refresh"),
    path("auth/me/", views.MeView.as_view(), name="auth-me"),

    # ---- Wallet ----
    path("wallet/", views.WalletView.as_view(), name="wallet"),
    path("wallet/deposit/", views.WalletDepositView.as_view(), name="wallet-deposit"),
    path("wallet/withdraw/", views.WalletWithdrawView.as_view(), name="wallet-withdraw"),

    # ---- Dashboard & Tools ----
    path("dashboard/summary/", views.DashboardView.as_view(), name="dashboard-summary"),
    path("calculator/estimate/", views.InvestmentCalculatorView.as_view(), name="calculator-estimate"),
    path("advisor/dashboard/", views.AdvisorDashboardView.as_view(), name="advisor-dashboard"),

    # ---- Ops: KYC queue & batch runs (replace what would have been Celery beat jobs) ----
    path("ops/kyc-queue/", views.OpsKYCQueueView.as_view(), name="ops-kyc-queue"),
    path("ops/run-coupon-batch/", views.RunCouponBatchView.as_view(), name="ops-run-coupon-batch"),
    path("ops/run-reinvestment-batch/", views.RunReinvestmentBatchView.as_view(), name="ops-run-reinvestment-batch"),

    # ---- Secondary market buy action (kept outside router for a flatter URL) ----
    path("secondary-market/buy/", views.SecondaryMarketListingViewSet.as_view({"post": "buy"}), name="secondary-market-buy"),

    # ---- Router URLs ----
    path("", include(router.urls)),
]