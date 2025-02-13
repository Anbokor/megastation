import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Nombre de categoría")
    min_stock = models.PositiveIntegerField(default=1, verbose_name="Stock mínimo antes de alerta")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

def product_image_path(instance, filename):
    """Функция для хранения изображений в каталоге 'products/' с уникальным именем файла."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'products/{instance.id}/{filename}'

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre del producto")
    description = models.TextField(blank=True, verbose_name="Descripción")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio")
    stock = models.PositiveIntegerField(verbose_name="Stock disponible")
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Código de barras")
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, verbose_name="Imagen del producto", default="default_product.jpg")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="Categoría")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

class StockMovement(models.Model):
    """
    ✅ Модель учета движения товаров на складе.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    change = models.IntegerField(verbose_name="Cambio en stock")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de movimiento")
    reason = models.CharField(max_length=255, verbose_name="Razón de cambio")

    def __str__(self):
        return f"{self.product.name} - {self.change} unidades ({self.reason})"

    class Meta:
        ordering = ["-created_at"]
