import pytest
import uuid
from rest_framework import status
from inventory.models import SalesPoint, Stock, StockMovement
from store.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def authenticated_client():
    """Фикстура для аутентифицированного клиента."""
    client = pytest.importorskip("rest_framework.test").APIClient()
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(username=unique_username, password="testpass")
    client.force_authenticate(user=user)
    return client, user

@pytest.mark.django_db(transaction=True)
def test_get_sales_points(authenticated_client):
    """Проверяет GET /sales-points/ для обычного пользователя."""
    client, user = authenticated_client
    sp1 = SalesPoint.objects.create(name="Store 1")
    sp2 = SalesPoint.objects.create(name="Store 2")
    sp1.administrators.add(user)
    sp2.sellers.add(user)
    response = client.get("/api/inventory/sales-points/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2
    assert {sp["name"] for sp in response.json()} == {"Store 1", "Store 2"}

@pytest.mark.django_db(transaction=True)
def test_get_sales_points_staff(authenticated_client):
    """Проверяет GET /sales-points/ для staff-пользователя."""
    client, _ = authenticated_client
    staff_username = f"staff_{uuid.uuid4().hex[:8]}"
    staff = User.objects.create_user(username=staff_username, password="staffpass", is_staff=True)
    client.force_authenticate(user=staff)
    SalesPoint.objects.create(name="Store 1")
    SalesPoint.objects.create(name="Store 2")
    response = client.get("/api/inventory/sales-points/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2

@pytest.mark.django_db(transaction=True)
def test_create_sales_point(authenticated_client):
    """Проверяет POST /sales-points/ и добавление администратора."""
    client, user = authenticated_client
    data = {"name": "New Store"}
    response = client.post("/api/inventory/sales-points/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    sales_point = SalesPoint.objects.get(name="New Store")
    assert user in sales_point.administrators.all()

@pytest.mark.django_db(transaction=True)
def test_get_stock_list(authenticated_client):
    """Проверяет GET /stock/."""
    client, _ = authenticated_client
    category = Category.objects.create(name="Tablets")
    product = Product.objects.create(name="iPad Pro", category=category, price=1500)
    sales_point = SalesPoint.objects.create(name="Retail Store")
    Stock.objects.create(product=product, sales_point=sales_point, quantity=5)
    response = client.get("/api/inventory/stock/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["product_name"] == "iPad Pro"

@pytest.mark.django_db(transaction=True)
def test_get_stock_movements(authenticated_client):
    """Проверяет GET /stock-movements/."""
    client, _ = authenticated_client
    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(name="MacBook", category=category, price=2000)
    sales_point = SalesPoint.objects.create(name="Store")
    Stock.objects.create(product=product, sales_point=sales_point, quantity=10)
    StockMovement.objects.create(product=product, sales_point=sales_point, change=-3, reason="Sale")
    response = client.get("/api/inventory/stock-movements/")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["reason"] == "Sale"

@pytest.mark.django_db(transaction=True)
def test_create_stock_movement(authenticated_client):
    """Проверяет POST /stock-movements/."""
    client, _ = authenticated_client
    category = Category.objects.create(name="Phones")
    product = Product.objects.create(name="iPhone", category=category, price=1000)
    sales_point = SalesPoint.objects.create(name="Shop")
    Stock.objects.create(product=product, sales_point=sales_point, quantity=10)
    data = {"product": product.id, "sales_point": sales_point.id, "change": -5, "reason": "Sale"}
    response = client.post("/api/inventory/stock-movements/", data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert StockMovement.objects.count() == 1
    assert Stock.objects.get(product=product).quantity == 10  # Количество не меняется автоматически