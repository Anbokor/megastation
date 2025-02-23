import pytest
import os
from django.conf import settings
from store.models import Product, Category
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage

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
    ✅ Проверяем создание товара.
    """
    category = Category.objects.create(name="Smartphones")
    product = Product.objects.create(
        name="iPhone 13",
        description="Nuevo iPhone con tecnología avanzada.",
        price=999.99,
        barcode="123456789",
        category=category
    )

    assert product.name == "iPhone 13"
    assert product.price == 999.99
    assert product.category == category

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
    ✅ Проверяем загрузку изображения и его удаление после теста.
    """
    category = Category.objects.create(name="Tablets")
    image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")

    product = Product.objects.create(name="iPad", price=500, category=category, image=image)

    assert product.image.name.startswith("products/")

    # ✅ Удаляем файл после теста
    image_path = os.path.join(settings.MEDIA_ROOT, product.image.name)
    if os.path.exists(image_path):
        os.remove(image_path)

    # Также можно добавить `product.image.delete()` на случай использования `Storage`
    product.image.delete()

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