import pytest
from users.models import CustomUser

@pytest.mark.django_db
def test_create_user():
    """Test de creación de usuario"""
    CustomUser.objects.all().delete()  # Limpieza antes del test
    user = CustomUser.objects.create_user(username="testuser", password="securepass")
    assert user.username == "testuser"
    assert user.check_password("securepass")
    assert user.is_active

@pytest.mark.django_db
def test_create_admin():
    """Test de creación de administrador"""
    CustomUser.objects.all().delete()  # Limpieza antes del test
    admin = CustomUser.objects.create_superuser(username="admin", password="adminpass")
    assert admin.is_superuser
    assert admin.is_staff

@pytest.mark.django_db
def test_user_roles():
    """Test de roles de usuario"""
    CustomUser.objects.all().delete()  # Limpieza перед тест
    user = CustomUser.objects.create_user(username="client", role=CustomUser.Role.CUSTOMER)
    assert user.role == CustomUser.Role.CUSTOMER  # Check role instead of is_customer