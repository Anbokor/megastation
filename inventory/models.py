from django.db import models
from store.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class SalesPoint(models.Model):
    """✅ Точка продаж с несколькими администраторами и продавцами."""
    name = models.CharField(max_length=255, verbose_name="Nombre del punto de venta")
    administrators = models.ManyToManyField(User, related_name="managed_sales_points", verbose_name="Administradores")
    sellers = models.ManyToManyField(User, related_name="sales_points", verbose_name="Vendedores")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Punto de venta"
        verbose_name_plural = "Puntos de venta"

class Stock(models.Model):
    """✅ Теперь `sales_point` временно получает `default=1`, чтобы миграция прошла"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_info")
    sales_point = models.ForeignKey(
        "SalesPoint", on_delete=models.CASCADE, related_name="stock", verbose_name="Punto de venta", default=1
    )
    quantity = models.PositiveIntegerField(default=0)
    reserved_quantity = models.PositiveIntegerField(default=0)  # Добавляем поле для резервирования
    low_stock_threshold = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    def is_low_stock(self):
        """Returns True if stock is below the threshold."""
        return self.quantity <= self.low_stock_threshold

    def adjust_stock(self, change, reason="Ajuste manual"):
        """
        ✅ Удобный метод для изменения `Stock` с логированием.
        """
        if not self.sales_point:
            raise ValueError(f"No se puede ajustar el stock porque el punto de venta no está asignado.")

        if self.quantity + change < 0:
            raise ValueError(f"No hay suficiente stock de {self.product.name} en {self.sales_point.name}.")

        self.quantity += change
        self.save()

        StockMovement.objects.create(
            product=self.product,
            sales_point=self.sales_point,
            change=change,
            reason=reason
        )

    def __str__(self):
        return f"{self.product.name} - {self.sales_point.name} - {self.quantity} en stock"

    class Meta:
        unique_together = ("product", "sales_point")

class StockMovement(models.Model):
    """✅ Логируем изменения на складе (теперь учитывает `SalesPoint`)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sales_point = models.ForeignKey(
        "SalesPoint", on_delete=models.CASCADE, related_name="stock_movements", verbose_name="Punto de venta"
    )
    change = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product.name} ({self.sales_point.name}): {self.change} ({self.reason})"

    class Meta:
        ordering = ["-created_at"]