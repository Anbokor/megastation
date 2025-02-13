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

from rest_framework.permissions import BasePermission

class CanAdvanceOrderStatus(BasePermission):
    """
    Allows sellers to move order status forward but not backward.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller

    def has_object_permission(self, request, view, obj):
        if request.method not in ["PATCH", "PUT"]:
            return False  # Only allow updates

        new_status = request.data.get("status")
        allowed_transitions = {
            "pendiente": "en proceso",
            "en proceso": "enviado",
        }
        return obj.status in allowed_transitions and allowed_transitions[obj.status] == new_status
