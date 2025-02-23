import pytest
from users.models import CustomUser


@pytest.mark.django_db
def test_create_user():
    CustomUser.objects.all().delete()  # Очистка пользователей перед тестом
    user = CustomUser.objects.create_user(username="testuser", password="securepass")

    assert user.username == "testuser"
    assert user.check_password("securepass")
    assert user.is_active


@pytest.mark.django_db
def test_create_admin():
    CustomUser.objects.all().delete()  # Очистка перед тестом
    admin = CustomUser.objects.create_superuser(username="admin", password="adminpass")

    assert admin.is_superuser
    assert admin.is_staff


@pytest.mark.django_db
def test_user_roles():
    CustomUser.objects.all().delete()  # Очистка перед тестом
    user = CustomUser.objects.create_user(username="client", role=CustomUser.Role.CUSTOMER)

    assert user.is_customer
    assert not user.is_admin
