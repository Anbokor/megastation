from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Categoría")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Nombre del producto")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Categoría")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio (ARS)")
    stock = models.IntegerField(default=0, verbose_name="Stock disponible")
    barcode = models.CharField(max_length=50, unique=True, verbose_name="Código de barras")

    def __str__(self):
        return f"{self.name} - {self.price} ARS"

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
