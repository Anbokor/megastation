import pytest
from rest_framework.exceptions import ValidationError
from datetime import timezone
from inventory.models import Stock, StockMovement, SalesPoint
from store.models import Product, Category
from inventory.serializers import StockSerializer, StockMovementSerializer

@pytest.mark.django_db(transaction=True)
def test_stock_serializer():
    """Проверяет сериализацию StockSerializer."""
    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(name="MacBook Pro", category=category, price=2000)
    sales_point = SalesPoint.objects.create(name="Main Warehouse")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=5, low_stock_threshold=10)
    serializer = StockSerializer(stock)
    expected_data = {
        "product": product.id,
        "product_name": "MacBook Pro",
        "category_name": "Laptops",
        "quantity": 5,
        "low_stock_threshold": 10,
        "is_low_stock": True  # < в сериализаторе
    }
    assert serializer.data == expected_data

@pytest.mark.django_db(transaction=True)
def test_stock_movement_serializer():
    """Проверяет сериализацию StockMovementSerializer."""
    category = Category.objects.create(name="Accessories")
    product = Product.objects.create(name="AirPods", category=category, price=200)
    sales_point = SalesPoint.objects.create(name="Retail Store")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=10, low_stock_threshold=5)
    movement = StockMovement.objects.create(product=product, sales_point=sales_point, change=-3, reason="Venta")
    serializer = StockMovementSerializer(movement)
    # Приводим формат времени к тому, что возвращает сериализатор (Z вместо +00:00)
    expected_created_at = movement.created_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    expected_data = {
        "id": movement.id,
        "product": product.id,
        "product_name": "AirPods",
        "category_name": "Accessories",
        "sales_point": sales_point.id,
        "change": -3,
        "created_at": expected_created_at,
        "reason": "Venta"
    }
    assert serializer.data == expected_data

@pytest.mark.django_db(transaction=True)
def test_stock_movement_serializer_validation_negative():
    """Проверяет валидацию на отрицательный запас."""
    category = Category.objects.create(name="Tablets")
    product = Product.objects.create(name="iPad", category=category, price=500)
    sales_point = SalesPoint.objects.create(name="Online Store")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=5)
    data = {"product": product.id, "sales_point": sales_point.id, "change": -10, "reason": "Venta"}
    serializer = StockMovementSerializer(data=data)
    with pytest.raises(ValidationError, match="El stock no puede ser negativo"):
        serializer.is_valid(raise_exception=True)

@pytest.mark.django_db(transaction=True)
def test_stock_serializer_low_stock_flag():
    """Проверяет флаг is_low_stock в StockSerializer."""
    category = Category.objects.create(name="Smartphones")
    product = Product.objects.create(name="Samsung Galaxy", category=category, price=1000)
    sales_point = SalesPoint.objects.create(name="Warehouse")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=5, low_stock_threshold=5)
    serializer = StockSerializer(stock)
    assert serializer.data["is_low_stock"] == False  # <, а не <=
    stock.quantity = 4
    stock.save()
    serializer = StockSerializer(stock)
    assert serializer.data["is_low_stock"] == True

@pytest.mark.django_db(transaction=True)
def test_stock_movement_serializer_zero_change():
    """Проверяет валидацию на change=0."""
    category = Category.objects.create(name="Consolas")
    product = Product.objects.create(name="PlayStation 5", category=category, price=800)
    sales_point = SalesPoint.objects.create(name="Game Store")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=5)
    data = {"product": product.id, "sales_point": sales_point.id, "change": 0, "reason": "Testing"}
    serializer = StockMovementSerializer(data=data)
    with pytest.raises(ValidationError, match="El cambio en stock no puede ser cero"):
        serializer.is_valid(raise_exception=True)