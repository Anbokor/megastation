import pytest
import uuid
from inventory.models import SalesPoint, Stock, StockMovement
from store.models import Product, Category
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db(transaction=True)
def test_create_sales_point():
    """Проверяет создание точки продаж и связь с пользователями."""
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    user = User.objects.create_user(username=unique_username, password="testpass")
    sales_point = SalesPoint.objects.create(name="Test Store")
    sales_point.administrators.add(user)
    assert sales_point.name == "Test Store"
    assert user in sales_point.administrators.all()

@pytest.mark.django_db(transaction=True)
def test_create_stock():
    """Проверяет создание склада и его свойства."""
    category = Category.objects.create(name="Smartphones")
    product = Product.objects.create(name="iPhone 14", category=category, price=1000)
    sales_point = SalesPoint.objects.create(name="Warehouse")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=10, low_stock_threshold=5)
    assert stock.quantity == 10
    assert stock.is_low_stock() == False

@pytest.mark.django_db(transaction=True)
def test_create_stock_movement():
    """Проверяет создание перемещения товара."""
    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(name="MacBook Pro", category=category, price=2000)
    sales_point = SalesPoint.objects.create(name="Main Store")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=10)
    movement = StockMovement.objects.create(product=product, sales_point=sales_point, change=-2, reason="Venta")
    assert movement.change == -2
    assert str(movement) == "MacBook Pro (Main Store): -2 (Venta)"