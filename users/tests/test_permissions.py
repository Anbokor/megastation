import pytest
from rest_framework.test import APIClient
from users.models import CustomUser
from inventory.models import SalesPoint  # Added import

@pytest.mark.django_db
class TestPermissions:
    def test_admin_access(self):
        """Test de acceso de administrador"""
        admin = CustomUser.objects.create_user(
            username='admin',
            password='admin123',
            role='admin'
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        response = client.get('/api/analytics/')
        assert response.status_code == 200

    def test_store_admin_access(self):
        """Test de acceso de administrador de tienda"""
        sales_point = SalesPoint.objects.create(name="Store1")  # Added sales_point
        store_admin = CustomUser.objects.create_user(
            username='store_admin',
            password='store123',
            role='store_admin',
            sales_point=sales_point  # Assigned sales_point
        )
        client = APIClient()
        client.force_authenticate(user=store_admin)
        response = client.get('/api/analytics/')
        assert response.status_code == 200

    def test_seller_access_restriction(self):
        """Test de restricción de acceso para vendedor"""
        seller = CustomUser.objects.create_user(
            username='seller',
            password='seller123',
            role='seller'
        )
        client = APIClient()
        client.force_authenticate(user=seller)
        response = client.get('/api/analytics/')
        assert response.status_code == 403