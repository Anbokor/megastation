import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import CustomUser
from users.serializers import UserSerializer, UserRegisterSerializer
from django.contrib.auth.hashers import check_password

@pytest.mark.django_db
def test_user_serializer_create():
    """
    ✅ Проверяем, что `UserSerializer` корректно создаёт пользователя с ролью customer по умолчанию.
    """
    data = {
        "username": "testuser",
        "password": "securepass123",
        "email": "testuser@example.com"
    }

    factory = APIRequestFactory()
    request = factory.get("/")  # Имитируем запрос без аутентификации

    serializer = UserSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), f"Validation errors: {serializer.errors}"

    user = serializer.save()
    assert user.username == "testuser"
    assert check_password("securepass123", user.password)
    assert user.email == "testuser@example.com"
    assert user.role == CustomUser.Role.CUSTOMER  # Роль по умолчанию
    assert user.is_active  # Пользователь должен быть активным
    assert not user.is_superuser  # Обычный пользователь не должен быть суперпользователем
    assert not user.is_staff  # Обычный пользователь не должен быть staff

    # Проверяем сериализованные данные
    serialized_data = UserSerializer(user, context={"request": request}).data
    expected_data = {
        "id": user.id,
        "username": "testuser",
        "email": "testuser@example.com",
        "role": "customer",
        "is_admin": False,
        "is_store_admin": False,
        "is_seller": False,
        "is_customer": True
    }
    assert serialized_data == expected_data, f"Expected {expected_data}, but got {serialized_data}"


@pytest.mark.django_db
def test_user_serializer_admin_role():
    """
    ✅ Проверяем, что `UserRegisterSerializer` создаёт только пользователей с ролью customer,
    даже если запрос от админа, так как регистрация через фронт доступна только для клиентов.
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
        # Убрали role, так как фронтенд не передаёт его
    }

    factory = APIRequestFactory()
    request = factory.post("/")  # Используем POST для имитации создания
    force_authenticate(request, admin)  # Имитируем запрос от админа

    # Используем UserRegisterSerializer для создания, как в API
    serializer = UserRegisterSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), f"Validation errors: {serializer.errors}"

    user = serializer.save()
    assert user.username == "storeadmin"
    assert check_password("storepass123", user.password)
    assert user.email == "storeadmin@example.com"
    assert user.role == CustomUser.Role.CUSTOMER  # Роль всегда customer для фронтенда
    assert user.is_active
    assert not user.is_superuser  # Пользователь не должен быть суперпользователем
    assert not user.is_staff  # Пользователь не должен быть staff

    # Проверяем сериализованные данные через UserSerializer
    serialized_data = UserSerializer(user, context={"request": request}).data
    expected_data = {
        "id": user.id,
        "username": "storeadmin",
        "email": "storeadmin@example.com",
        "role": "customer",
        "is_admin": False,
        "is_store_admin": False,
        "is_seller": False,
        "is_customer": True
    }
    assert serialized_data == expected_data, f"Expected {expected_data}, but got {serialized_data}"


@pytest.mark.django_db
def test_user_serializer_invalid_role():
    """
    ✅ Проверяем, что `UserRegisterSerializer` всегда создаёт пользователей с ролью customer,
    игнорируя попытки указать другую роль через фронтенд.
    """
    data = {
        "username": "seller",
        "password": "sellerpass123",
        "email": "seller@example.com"
        # Убрали role, так как фронтенд не передаёт его
    }

    factory = APIRequestFactory()
    request = factory.post("/")  # Используем POST для имитации создания
    force_authenticate(request, user=None)  # Имитируем запрос без аутентификации

    serializer = UserRegisterSerializer(data=data, context={"request": request})
    assert serializer.is_valid(), f"Validation errors: {serializer.errors}"

    user = serializer.save()
    assert user.role == CustomUser.Role.CUSTOMER  # Роль всегда customer для фронтенда


@pytest.mark.django_db
def test_user_serializer_update():
    """
    ✅ Проверяем, что `UserSerializer` не позволяет изменять роль при обновлении.
    """
    user = CustomUser.objects.create_user(
        username="testuser",
        password="securepass123",
        email="testuser@example.com"
    )

    data = {
        "username": "updateduser",
        "role": "admin"  # Проверка, что роль не изменится
    }

    factory = APIRequestFactory()
    request = factory.patch("/", user=user)  # Имитируем запрос на обновление
    force_authenticate(request, user)  # Убедимся, что пользователь аутентифицирован

    serializer = UserSerializer(user, data=data, partial=True, context={"request": request})
    assert serializer.is_valid(), f"Validation errors: {serializer.errors}"

    updated_user = serializer.save()
    assert updated_user.username == "updateduser"
    assert updated_user.role == CustomUser.Role.CUSTOMER  # Роль не должна измениться
    assert not updated_user.is_superuser
    assert not updated_user.is_staff


@pytest.mark.django_db
def test_user_serializer_password_hashing():
    """
    ✅ Проверяем, что `UserSerializer` корректно хеширует пароль.
    """
    data = {
        "username": "testpass",
        "password": "testpass123",
        "email": "testpass@example.com"
    }

    serializer = UserSerializer(data=data)
    assert serializer.is_valid(), f"Validation errors: {serializer.errors}"

    user = serializer.save()
    assert check_password("testpass123", user.password)
    assert not user.password.startswith("testpass123")  # Проверяем, что пароль не хранится в открытом виде