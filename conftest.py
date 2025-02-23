import pytest
from django.conf import settings
from rest_framework.test import APIClient
from users.models import CustomUser
from store.models import Product, Category
from inventory.models import Stock, SalesPoint


@pytest.fixture(scope="session")
def django_db_setup():
    """
    Используем SQLite в памяти для тестов.
    """
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        'ATOMIC_REQUESTS': True,
    }


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
    from inventory.models import Stock, SalesPoint
    sales_point = SalesPoint.objects.create(name="Main Warehouse")
    return Stock.objects.create(product=product, sales_point=sales_point, quantity=10)
