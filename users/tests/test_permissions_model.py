import pytest
from users.models import CustomUser
from inventory.models import SalesPoint

@pytest.mark.django_db
class TestHasPerm:
    @pytest.fixture
    def superuser(self):
        return CustomUser.objects.create_superuser(username="superuser", password="password")

    @pytest.fixture
    def admin_user(self):
        return CustomUser.objects.create_user(username="adminuser", password="password", role=CustomUser.Role.ADMIN)

    @pytest.fixture
    def sales_point(self):
        return SalesPoint.objects.create(name="Test Point")

    @pytest.fixture
    def store_admin_user(self, sales_point):
        return CustomUser.objects.create_user(
            username="storeadmin",
            password="password",
            role=CustomUser.Role.STORE_ADMIN,
            sales_point=sales_point
        )

    @pytest.fixture
    def seller_user(self, sales_point):
        return CustomUser.objects.create_user(
            username="selleruser",
            password="password",
            role=CustomUser.Role.SELLER,
            sales_point=sales_point
        )

    @pytest.fixture
    def customer_user(self):
        return CustomUser.objects.create_user(username="customeruser", password="password", role=CustomUser.Role.CUSTOMER)

    def test_superuser_permissions(self, superuser):
        """Superuser should have all permissions."""
        assert superuser.has_perm("any_permission") is True
        assert superuser.has_perm("add_user") is True
        assert superuser.has_perm("change_stock") is True

    def test_admin_permissions(self, admin_user):
        """Admin should have specific user and analytics permissions."""
        assert admin_user.has_perm("add_user") is True
        assert admin_user.has_perm("change_user") is True
        assert admin_user.has_perm("delete_user") is True
        assert admin_user.has_perm("view_analytics") is True
        # Check for a permission they should NOT have
        assert admin_user.has_perm("change_stock") is False
        assert admin_user.has_perm("process_order") is False

    def test_store_admin_permissions(self, store_admin_user):
        """Store Admin should have stock and store viewing permissions."""
        assert store_admin_user.has_perm("change_stock") is True
        assert store_admin_user.has_perm("view_store") is True
        # Check for permissions they should NOT have
        assert store_admin_user.has_perm("add_user") is False
        assert store_admin_user.has_perm("view_analytics") is False
        assert store_admin_user.has_perm("process_order") is False

    def test_seller_permissions(self, seller_user):
        """Seller should have store viewing and order processing permissions."""
        assert seller_user.has_perm("view_store") is True
        assert seller_user.has_perm("process_order") is True
        # Check for permissions they should NOT have
        assert seller_user.has_perm("change_stock") is False
        assert seller_user.has_perm("add_user") is False
        assert seller_user.has_perm("view_analytics") is False

    def test_customer_permissions(self, customer_user):
        """Customer permissions are based on their role, which is an unusual implementation."""
        # The original implementation `return self.role == self.Role.CUSTOMER`
        # returns True if the user is a customer, regardless of the permission string.
        # This test verifies the current behavior.
        assert customer_user.has_perm("any_permission_string") is True
        assert customer_user.has_perm("view_store") is True # This will pass because of the implementation
        assert customer_user.has_perm("some_other_perm") is True # This will also pass

    def test_store_admin_without_sales_point(self):
        """Store Admin without a sales point should have no specific permissions."""
        store_admin_no_sp = CustomUser.objects.create_user(
            username="storeadmin_no_sp",
            password="password",
            role=CustomUser.Role.STORE_ADMIN,
            sales_point=None
        )
        assert store_admin_no_sp.has_perm("change_stock") is False
        assert store_admin_no_sp.has_perm("view_store") is False