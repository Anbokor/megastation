import pytest
from store.models import Product, Category
from store.serializers import ProductSerializer, CategorySerializer
from inventory.models import Stock, StockMovement, SalesPoint
from inventory.serializers import StockMovementSerializer
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIRequestFactory
from django.utils.dateparse import parse_datetime


@pytest.mark.django_db
def test_category_serializer():
    """
    ✅ Проверяем, что `CategorySerializer` корректно сериализует данные.
    """
    category = Category.objects.create(name="Tablets")
    serializer = CategorySerializer(category)

    expected_data = {"id": category.id, "name": "Tablets"}
    assert serializer.data == expected_data


@pytest.mark.django_db
def test_product_serializer():
    """
    ✅ Проверяем, что `ProductSerializer` корректно сериализует данные.
    """
    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(name="MacBook Pro", price=2000, category=category, barcode="111222333")

    # 🔥 Создаем точку продаж перед созданием Stock
    sales_point = SalesPoint.objects.create(name="Retail Store")

    # 🔥 Теперь Stock создаётся корректно
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=5)

    factory = APIRequestFactory()
    request = factory.get("/")  # ✅ Имитируем запрос для `image_url`

    serializer = ProductSerializer(product, context={"request": request})

    expected_data = {
        "id": product.id,
        "name": "MacBook Pro",
        "description": "",
        "price": "2000.00",
        "stock": 5,  # ✅ Проверяем, что `get_stock` вернул правильное значение
        "barcode": "111222333",
        "image_url": request.build_absolute_uri("/media/default_product.jpg"),
    }

    # ✅ Проверяем наличие ключа image, если он есть в данных сериализатора, добавляем в expected_data
    if "image" in serializer.data:
        expected_data["image"] = request.build_absolute_uri("/media/default_product.jpg")

    assert serializer.data == expected_data



@pytest.mark.django_db
def test_product_serializer_with_image():
    """
    ✅ Проверяем, что `ProductSerializer` корректно формирует `image_url`.
    """
    category = Category.objects.create(name="Phones")
    image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
    product = Product.objects.create(name="iPhone", price=1000, category=category, image=image)

    factory = APIRequestFactory()
    request = factory.get("/")

    serializer = ProductSerializer(product, context={"request": request})

    assert serializer.data["image_url"] == request.build_absolute_uri(product.image.url)


@pytest.mark.django_db
def test_stock_movement_serializer():
    """
    ✅ Проверяем, что `StockMovementSerializer` корректно сериализует данные.
    """
    category = Category.objects.create(name="Accessories")
    product = Product.objects.create(name="AirPods", category=category, price=200)

    # ✅ Создаем точку продаж
    sales_point = SalesPoint.objects.create(name="Main Store")

    movement = StockMovement.objects.create(product=product, sales_point=sales_point, change=10, reason="Replenishment")

    serializer = StockMovementSerializer(movement)

    # ✅ Приводим `created_at` к `datetime`-объекту
    created_at_serialized = parse_datetime(serializer.data["created_at"])

    assert serializer.data["id"] == movement.id
    assert serializer.data["product"] == product.id
    assert serializer.data["product_name"] == "AirPods"
    assert serializer.data["category_name"] == "Accessories"
    assert serializer.data["change"] == 10
    assert created_at_serialized.replace(tzinfo=None) == movement.created_at.replace(tzinfo=None)  # ✅ Учитываем `tzinfo`
    assert serializer.data["reason"] == "Replenishment"


from rest_framework.exceptions import ValidationError

@pytest.mark.django_db
def test_stock_movement_serializer_validation():
    """
    ✅ Проверяем, что `StockMovementSerializer` выбрасывает ошибку, если `Stock.quantity` станет отрицательным.
    """
    category = Category.objects.create(name="Monitors")
    product = Product.objects.create(name="Dell Monitor", category=category, price=300)

    # ✅ Создаем точку продаж
    sales_point = SalesPoint.objects.create(name="Warehouse")

    # ✅ Добавляем `Stock`
    stock = Stock.objects.create(product=product, quantity=5, sales_point=sales_point)

    data = {
        "product": product.id,
        "sales_point": sales_point.id,
        "change": -10,  # ❌ Попытка сделать склад отрицательным
        "reason": "Sale",
    }

    serializer = StockMovementSerializer(data=data)

    # ✅ Проверяем, что валидация не проходит и выбрасывает ошибку
    with pytest.raises(ValidationError) as excinfo:
        serializer.is_valid(raise_exception=True)

    # ✅ Убеждаемся, что причина ошибки правильная
    assert "change" in excinfo.value.detail, "Ожидалась ошибка на поле 'change'"
    assert excinfo.value.detail["change"][0] == "El stock no puede ser negativo."