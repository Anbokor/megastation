import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from store.models import Category, Product
from inventory.models import Stock, SalesPoint
import uuid

User = get_user_model()

@pytest.fixture
def authenticated_client():
    """
    ✅ Фикстура для создания аутентифицированного клиента с пользователем и точкой продаж.
    """
    client = APIClient()
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(username=username, password="securepass")

    # ✅ Создаём точку продаж и привязываем её к пользователю
    sales_point = SalesPoint.objects.create(name="Central Store")
    user.sales_points.add(sales_point)

    client.force_authenticate(user=user)
    return client, user


@pytest.mark.django_db
def test_list_products(authenticated_client):
    """
    ✅ Тест получения списка товаров.
    """
    client, user = authenticated_client

    category = Category.objects.create(name="Smartphones")
    product = Product.objects.create(name="iPhone 13", category=category, price=999, barcode="111111")

    # ✅ Создаём складской запас с привязкой к точке продаж
    sales_point = user.sales_points.first()
    Stock.objects.create(product=product, quantity=5, sales_point=sales_point)

    url = reverse("store:product-list")
    response = client.get(url)

    assert response.status_code == 200
    assert any(p["name"] == "iPhone 13" for p in response.json())


@pytest.mark.django_db
def test_update_product(authenticated_client):
    """
    ✅ Тест обновления товара.
    """
    client, user = authenticated_client

    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(name="MacBook Air", category=category, price=1200, barcode="222222")

    # ✅ Привязываем продукт к точке продаж пользователя
    sales_point = user.sales_points.first()
    Stock.objects.create(product=product, sales_point=sales_point, quantity=10)

    url = reverse("store:product-detail", args=[product.id])
    response = client.patch(url, {"price": 1300})

    assert response.status_code == 200
    product.refresh_from_db()
    assert product.price == 1300


@pytest.mark.django_db
def test_delete_product(authenticated_client):
    """
    ✅ Тест удаления товара.
    """
    client, user = authenticated_client

    category = Category.objects.create(name="Smartwatches")
    product = Product.objects.create(name="Apple Watch", category=category, price=500, barcode="333333")

    # ✅ Привязываем продукт к точке продаж пользователя
    sales_point = user.sales_points.first()
    Stock.objects.create(product=product, sales_point=sales_point, quantity=5)

    url = reverse("store:product-detail", args=[product.id])
    response = client.delete(url)

    assert response.status_code == 204
    assert not Product.objects.filter(id=product.id).exists()


@pytest.mark.django_db
def test_low_stock_products(authenticated_client):
    """
    ✅ Тест получения товаров с низким запасом.
    """
    client, user = authenticated_client

    # 🔥 Делаем пользователя администратором
    user.is_staff = True
    user.save()

    category = Category.objects.create(name="Monitors", min_stock=5)
    product1 = Product.objects.create(name="Dell Monitor", category=category, price=300, barcode="444444")
    product2 = Product.objects.create(name="LG Monitor", category=category, price=250, barcode="555555")

    sales_point = user.sales_points.first()

    # ✅ Добавляем товары в склад с малым запасом, обязательно указываем `sales_point`
    Stock.objects.bulk_create([
        Stock(product=product1, quantity=3, sales_point=sales_point),
        Stock(product=product2, quantity=10, sales_point=sales_point)
    ])

    # ✅ Исправленный `reverse()`
    url = reverse("store:low-stock")

    response = client.get(url)

    assert response.status_code == 200
    products = response.json()

    assert any(p["name"] == "Dell Monitor" for p in products)
    assert not any(p["name"] == "LG Monitor" for p in products)
