import pytest
import os
from django.conf import settings
from store.models import Product, Category
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import TemporaryUploadedFile

@pytest.mark.django_db
def test_create_category():
    """
    ✅ Проверяем создание категории.
    """
    category = Category.objects.create(name="Smartphones")
    assert category.name == "Smartphones"
    assert category.min_stock == 1  # Значение по умолчанию

@pytest.mark.django_db
def test_unique_category_name():
    """
    ✅ Проверяем уникальность имени категории.
    """
    Category.objects.create(name="Laptops")

    with pytest.raises(IntegrityError):
        Category.objects.create(name="Laptops")

@pytest.mark.django_db
def test_min_stock_default():
    """
    ✅ Проверяем значение `min_stock` по умолчанию.
    """
    category = Category.objects.create(name="Tablets")
    assert category.min_stock == 1

@pytest.mark.django_db
def test_create_product():
    """
    Test de creación de producto
    """
    import uuid
    unique_barcode = f"123456789-{uuid.uuid4().hex[:8]}"
    category = Category.objects.create(name="Smartphones")
    product = Product.objects.create(
        name="iPhone 13",
        description="Nuevo iPhone con tecnología avanzada.",
        price=999.99,
        barcode=unique_barcode,
        category=category
    )

@pytest.mark.django_db
def test_product_category_relation():
    """
    ✅ Проверяем связь товара с категорией.
    """
    category = Category.objects.create(name="Laptops")
    product = Product.objects.create(name="MacBook Pro", price=2000, category=category)

    assert product.category.name == "Laptops"

@pytest.mark.django_db
def test_unique_barcode():
    """
    ✅ Проверяем уникальность кода `barcode`.
    """
    Product.objects.create(name="Galaxy S21", price=799, barcode="987654321")

    with pytest.raises(IntegrityError):
        Product.objects.create(name="Galaxy S22", price=899, barcode="987654321")

@pytest.mark.django_db
def test_product_image_upload():
    """
    ✅ Проверяем, что изображение продукта корректно загружается.
    """
    category = Category.objects.create(name="Electronics")

    # Создаем временный файл
    test_image = TemporaryUploadedFile(
        name="default_product.jpg",
        content_type="image/jpeg",
        size=1024,
        charset=None
    )
    test_image.write(b"file_content")  # Записываем тестовые данные
    test_image.seek(0)  # Возвращаемся в начало файла

    product = Product.objects.create(
        name="Test Product",
        price=100.00,
        category=category,
        image=test_image
    )

    # Проверяем, что путь начинается с 'products/temp/' и заканчивается '.jpg'
    assert product.image.name.startswith("products/temp/")
    assert product.image.name.endswith(".jpg")

    # Файл автоматически удаляется благодаря TemporaryUploadedFile

@pytest.mark.django_db
def test_category_deletion_sets_null():
    """
    ✅ Проверяем, что при удалении категории поле `category` в `Product` становится `NULL`.
    """
    category = Category.objects.create(name="Monitors")
    product = Product.objects.create(name="Dell Monitor", price=300, category=category)

    category.delete()
    product.refresh_from_db()

    assert product.category is None