"""
api/permissions.py
Role-based access control (RBAC) permission classes for BondVault.
"""

from rest_framework import permissions

from .models import User


class IsInvestor(permissions.BasePermission):
    message = "Only investors can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.INVESTOR)


class IsAdvisor(permissions.BasePermission):
    message = "Only investment advisors can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.ADVISOR)


class IsOps(permissions.BasePermission):
    message = "Only the operations team can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.OPS)


class IsSuperAdmin(permissions.BasePermission):
    message = "Only a super administrator can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and (request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )


class IsOpsOrAdmin(permissions.BasePermission):
    message = "Only operations staff or an administrator can perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in (User.Role.OPS, User.Role.ADMIN)
        )


class IsAdvisorOpsOrAdmin(permissions.BasePermission):
    """Staff roles that may view (but not necessarily move money for) investors."""
    message = "You do not have staff access."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.role in (User.Role.ADVISOR, User.Role.OPS, User.Role.ADMIN)
        )


class IsKYCVerified(permissions.BasePermission):
    message = "Your KYC verification must be approved before you can invest."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_kyc_verified)


class IsOwnerInvestor(permissions.BasePermission):
    """
    Object-level permission: only the investor who owns the object (or staff)
    may view/edit it. Assumes the object has an `investor` FK to InvestorProfile,
    or is itself an InvestorProfile.
    """
    message = "You do not have permission to access this record."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.role in (User.Role.OPS, User.Role.ADMIN):
            return True
        if user.role == User.Role.ADVISOR:
            investor = obj if hasattr(obj, "user") else getattr(obj, "investor", None)
            return bool(investor and investor.advisor_id == user.id)

        owner_profile = obj if hasattr(obj, "user") else getattr(obj, "investor", None)
        return bool(owner_profile and owner_profile.user_id == user.id)


class ReadOnlyOrIsOpsAdmin(permissions.BasePermission):
    """Allows safe (GET/HEAD/OPTIONS) methods to any authenticated user,
    but restricts write operations to Ops/Admin. Useful for market data
    endpoints like Security / BondAuction that investors browse but do
    not directly edit."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in (User.Role.OPS, User.Role.ADMIN)