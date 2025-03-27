import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser
from users.serializers import UserSerializer, UserRegisterSerializer
from django.contrib.auth.hashers import check_password

@pytest.mark.django_db
def test_user_serializer_create():
    """
    Test de creación de usuario con UserSerializer
    """
    data = {
        "username": "testuser",
        "password": "securepass123",
        "email": "testuser@example.com"
    }
    factory = APIRequestFactory()
    request = factory.get("/")
    serializer = UserSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), f"Errores de validación: {serializer.errors}"
    user = serializer.save()
    assert user.username == "testuser"
    assert check_password("securepass123", user.password)
    assert user.email == "testuser@example.com"
    assert user.role == CustomUser.Role.CUSTOMER
    assert user.is_active
    assert not user.is_superuser
    assert not user.is_staff
    serialized_data = UserSerializer(user, context={"request": request}).data
    expected_data = {
        "id": user.id,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": "customer"
    }
    assert serialized_data == expected_data, f"Esperado {expected_data}, pero se obtuvo {serialized_data}"

@pytest.mark.django_db
def test_user_serializer_admin_role():
    """
    Test de creación de usuario con UserRegisterSerializer por admin
    """
    admin = CustomUser.objects.create_superuser(
        username="admin",
        password="adminpass123",
        email="admin@example.com"
    )
    data = {
        "username": "storeadmin",
        "password": "storepass123",
        "email": "storeadmin@example.com"
    }
    factory = APIRequestFactory()
    request = factory.post("/")
    force_authenticate(request, admin)
    serializer = UserRegisterSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), f"Errores de validación: {serializer.errors}"
    user = serializer.save()
    assert user.username == "storeadmin"
    assert check_password("storepass123", user.password)
    assert user.email == "storeadmin@example.com"
    assert user.role == CustomUser.Role.CUSTOMER
    assert user.is_active
    assert not user.is_superuser
    assert not user.is_staff
    serialized_data = UserSerializer(user, context={"request": request}).data
    expected_data = {
        "id": user.id,
        "username": "storeadmin",
        "email": "storeadmin@example.com",
        "role": "customer"
    }
    assert serialized_data == expected_data, f"Esperado {expected_data}, pero se obtuvo {serialized_data}"

@pytest.mark.django_db
def test_user_serializer_invalid_role():
    """
    Test de rol inválido con UserRegisterSerializer
    """
    data = {
        "username": "seller",
        "password": "sellerpass123",
        "email": "seller@example.com"
    }
    factory = APIRequestFactory()
    request = factory.post("/")
    force_authenticate(request, user=None)
    serializer = UserRegisterSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), f"Errores de validación: {serializer.errors}"
    user = serializer.save()
    assert user.role == CustomUser.Role.CUSTOMER

@pytest.mark.django_db
def test_user_serializer_update():
    """
    Test de actualización de usuario con UserSerializer
    """
    user = CustomUser.objects.create_user(
        username="testuser",
        password="securepass123",
        email="testuser@example.com"
    )
    data = {
        "username": "updateduser",
        "role": "admin"  # Role should not change
    }
    factory = APIRequestFactory()
    request = factory.patch("/")
    force_authenticate(request, user)
    serializer = UserSerializer(user, data=data, partial=True, context={"request": request})
    assert serializer.is_valid(), f"Errores de validación: {serializer.errors}"
    updated_user = serializer.save()
    assert updated_user.username == "updateduser"
    assert updated_user.role == CustomUser.Role.CUSTOMER
    assert not updated_user.is_superuser
    assert not updated_user.is_staff

@pytest.mark.django_db
def test_user_serializer_password_hashing():
    """
    Test de hash de contraseña con UserSerializer
    """
    data = {
        "username": "testpass",
        "password": "testpass123",
        "email": "testpass@example.com"
    }
    serializer = UserSerializer(data=data)
    assert serializer.is_valid(), f"Errores de validación: {serializer.errors}"
    user = serializer.save()
    assert check_password("testpass123", user.password)
    assert not user.password.startswith("testpass123")