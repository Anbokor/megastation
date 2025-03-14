from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superuser'

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'admin'

class IsStoreAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'store_admin'

class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'seller'

class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'customer'

class CanAdvanceOrderStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.role in ['admin', 'store_admin'])