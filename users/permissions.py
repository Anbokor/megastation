from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    ✅ Разрешает доступ только администраторам.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin()

class IsStoreAdmin(permissions.BasePermission):
    """
    ✅ Разрешает доступ только администраторам магазинов.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_store_admin()

class IsSeller(permissions.BasePermission):
    """
    ✅ Разрешает доступ только продавцам.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_seller()

class IsCustomer(permissions.BasePermission):
    """
    ✅ Разрешает доступ только покупателям.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_customer()
