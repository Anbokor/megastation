from rest_framework import permissions
import logging

logger = logging.getLogger(__name__)

class IsSuperuser(permissions.BasePermission):
    """Allows access only to superusers."""
    def has_permission(self, request, view):
        # DEBUG: Log user attributes to solve permission issue
        logger.info(f"Checking IsSuperuser for user: {request.user}")
        logger.info(f"User is_authenticated: {request.user.is_authenticated}")
        logger.info(f"User is_superuser flag: {request.user.is_superuser}")
        if hasattr(request.user, 'role'):
            logger.info(f"User role attribute: {request.user.role}")
        else:
            logger.info("User does not have a 'role' attribute.")
            
        # Correctly check the standard `is_superuser` flag.
        return request.user and request.user.is_authenticated and request.user.is_superuser

class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'admin'

class IsStoreAdmin(permissions.BasePermission):
    """Allows access only to store admin users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'store_admin'

class IsSeller(permissions.BasePermission):
    """Allows access only to seller users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'seller'

class IsCustomer(permissions.BasePermission):
    """Allows access only to customer users."""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and hasattr(request.user, "role") and request.user.role == 'customer'

class CanAdvanceOrderStatus(permissions.BasePermission):
    """Allows advancing order status to staff members."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        # Superuser has all permissions
        if request.user.is_superuser:
            return True
        # Check for staff roles
        if hasattr(request.user, 'role'):
            return request.user.role in ['admin', 'store_admin']
        return False
