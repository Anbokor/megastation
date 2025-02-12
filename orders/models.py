from django.db import models
from users.models import CustomUser
from store.models import Product
from django.utils.timezone import now

class Order(models.Model):
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Usuario")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente', verbose_name="Estado")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    def __str__(self):
        return f"Orden {self.id} - {self.user.username} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Orden {self.order.id})"

    class Meta:
        verbose_name = "Artículo en la orden"
        verbose_name_plural = "Artículos en la orden"
