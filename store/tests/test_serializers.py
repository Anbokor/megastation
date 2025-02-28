import pytest
from store.models import Product, Category
from store.serializers import ProductSerializer
from inventory.models import Stock, SalesPoint
from rest_framework.test import APIRequestFactory
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import TemporaryUploadedFile

@pytest.mark.django_db
def test_product_serializer():
    """
    ✅ Проверяем, что `ProductSerializer` корректно сериализует данные.
    """
    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(
        name="MacBook Pro",
        price=2000,
        category=category,
        barcode="111222333"
    )

    sales_point = SalesPoint.objects.create(name="Retail Store")
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=5)

    factory = APIRequestFactory()
    request = factory.get("/")  # Имитируем запрос для `image_url`

    serializer = ProductSerializer(product, context={"request": request})

    expected_data = {
        "id": product.id,
        "name": "MacBook Pro",
        "description": "",
        "price": "2000.00",
        "stock": 5,
        "barcode": "111222333",
        "image": request.build_absolute_uri("/media/default_product.jpg"),
        "image_url": request.build_absolute_uri("/media/default_product.jpg"),
        "category_id": category.id
    }

    assert serializer.data == expected_data, f"Expected {expected_data}, but got {serializer.data}"

@pytest.mark.django_db
def test_product_serializer_with_image():
    """
    ✅ Проверяем, что `ProductSerializer` корректно формирует `image_url` и image.
    """
    category = Category.objects.create(name="Phones")
    sales_point = SalesPoint.objects.create(name="Tienda Principal")

    product = Product.objects.create(
        name="iPhone",
        description="",
        price=1000.00,
        category=category,
    )

    stock = Stock.objects.create(
        product=product,
        sales_point=sales_point,
        quantity=5
    )

    # Создаем временный файл
    test_image = TemporaryUploadedFile(
        name="default_product.jpg",
        content_type="image/jpeg",
        size=1024,
        charset=None
    )
    test_image.write(b"file_content")
    test_image.seek(0)

    product.image.save("test_product.jpg", test_image, save=True)

    factory = APIRequestFactory()
    request = factory.get("/")

    serializer = ProductSerializer(product, context={"request": request})

    expected_data = {
        "id": product.id,
        "name": "iPhone",
        "description": "",
        "price": "1000.00",
        "stock": 5,
        "barcode": None,
        "image": request.build_absolute_uri(product.image.url),
        "image_url": request.build_absolute_uri(product.image.url),
        "category_id": category.id
    }

    assert serializer.data == expected_data, f"Expected {expected_data}, but got {serializer.data}"

    # Файл автоматически удаляется благодаря TemporaryUploadedFile

@pytest.mark.django_db
def test_product_serializer_no_stock():
    """
    ✅ Проверяем, что `ProductSerializer` корректно обрабатывает продукт без стока.
    """
    category = Category.objects.create(name="Notebooks")
    product = Product.objects.create(
        name="Dell Inspiron",
        description="Laptop económico",
        price=599.00,
        category=category,
        barcode="555555555"
    )

    factory = APIRequestFactory()
    request = factory.get("/")

    serializer = ProductSerializer(product, context={"request": request})

    expected_data = {
        "id": product.id,
        "name": "Dell Inspiron",
        "description": "Laptop económico",
        "price": "599.00",
        "stock": 0,
        "barcode": "555555555",
        "image": request.build_absolute_uri("/media/default_product.jpg"),
        "image_url": request.build_absolute_uri("/media/default_product.jpg"),
        "category_id": category.id
    }

    assert serializer.data == expected_data, f"Expected {expected_data}, but got {serializer.data}"