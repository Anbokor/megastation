from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsAdmin(permissions.BasePermission):
    """✅ Разрешает доступ только администраторам системы."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'admin'


class IsStoreAdmin(permissions.BasePermission):
    """✅ Разрешает доступ только администраторам магазинов."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'store_admin'


class IsSeller(permissions.BasePermission):
    """✅ Разрешает доступ только продавцам."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'seller'


class IsCustomer(permissions.BasePermission):
    """✅ Разрешает доступ только покупателям."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'customer'

class CanAdvanceOrderStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff  # Упрощаем для теста
