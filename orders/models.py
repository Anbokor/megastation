from django.db import models
from users.models import CustomUser
from store.models import Product
from inventory.models import Stock, SalesPoint # Import SalesPoint
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class Order(models.Model):
    # FIX: Add all possible statuses to the choices
    STATUS_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En proceso'),
        ('enviado', 'Enviado'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
        ('fallido', 'Fallido'),
    )
    PAYMENT_CHOICES = (
        ('card', 'Tarjeta'),
        ('mercado_pago', 'Mercado Pago'),
        ('cash', 'Efectivo'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Usuario")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente', verbose_name="Estado")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio total")
    total_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo total")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='card', verbose_name="Método de pago")

    def __str__(self):
        return f"Orden {self.id} - {self.user.username} - {self.get_status_display()}"

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"

class OrderItem(models.Model):
    DELIVERY_CHOICES = (
        ('Entrega inmediata', 'Entrega inmediata'),
        ('Entrega en 5-7 días', 'Entrega en 5-7 días'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # The sales_point the item was sold from. This is the correct way to track sales.
    sales_point = models.ForeignKey(SalesPoint, on_delete=models.SET_NULL, null=True, blank=True, related_name="order_items")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена в момент продажи")
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Себестоимость в момент продажи")
    delivery_time = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='Entrega inmediata', verbose_name="Tiempo de entrega")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Orden {self.order.id})"

    class Meta:
        verbose_name = "Artículo en la orden"
        verbose_name_plural = "Artículos en la orden"
