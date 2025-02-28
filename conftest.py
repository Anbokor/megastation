import pytest
import tempfile
import shutil
from django.conf import settings
from rest_framework.test import APIClient
from users.models import CustomUser
from store.models import Product, Category
from inventory.models import Stock, SalesPoint

@pytest.fixture(scope="session")
def django_db_setup():
    """
    Используем реальную базу данных (PostgreSQL) для тестов, чтобы данные сохранялись.
    """
    # Не переопределяем БД, оставляем PostgreSQL из settings.py
    pass


@pytest.fixture(autouse=True)
def temp_media_root():
    """
    Автоматически устанавливает временную директорию для MEDIA_ROOT в тестах и очищает её после завершения.
    """
    media_root = tempfile.mkdtemp()  # Создаем временную директорию
    original_media_root = settings.MEDIA_ROOT
    settings.MEDIA_ROOT = media_root

    yield  # Выполняем тест

    # Очищаем временную директорию после теста
    shutil.rmtree(media_root, ignore_errors=True)
    settings.MEDIA_ROOT = original_media_root  # Восстанавливаем оригинальный путь


@pytest.fixture
def authenticated_client(db):
    """
    ✅ Создает аутентифицированного пользователя и клиент API.
    """
    user, created = CustomUser.objects.get_or_create(
        username="testuser",
        defaults={"password": "testpassword", "role": CustomUser.Role.SELLER},
    )

    if not created:
        user.set_password("testpassword")
        user.save()

    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def product(db):
    """
    ✅ Создает тестовый товар.
    """
    category, _ = Category.objects.get_or_create(name="Smartphones")
    return Product.objects.create(name="iPhone 15", category=category, price=1200)


@pytest.fixture
def stock(db, product):
    """
    ✅ Создает тестовый запас для товара.
    """
    sales_point = SalesPoint.objects.create(name="Main Warehouse")
    return Stock.objects.create(product=product, sales_point=sales_point, quantity=10)