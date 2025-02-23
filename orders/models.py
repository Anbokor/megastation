from django.db import models
from users.models import CustomUser
from store.models import Product
from inventory.models import Stock
from django.utils.timezone import now
from django.core.exceptions import ValidationError

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

    def update_status(self, new_status):
        if self.status == "pendiente" and new_status == "en_proceso":
            for item in self.items.all():
                stock = Stock.objects.get(product=item.product)
                if stock.reserved_quantity < item.quantity:
                    raise ValidationError(f"Error en stock de {item.product.name}.")
                stock.reserved_quantity -= item.quantity
                stock.save()

        elif self.status == "pendiente" and new_status == "cancelado":
            for item in self.items.all():
                stock = Stock.objects.get(product=item.product)
                stock.quantity += item.quantity
                stock.reserved_quantity -= item.quantity
                stock.save()

        elif self.status == "en_proceso" and new_status == "cancelado":
            for item in self.items.all():
                stock = Stock.objects.get(product=item.product)
                stock.quantity += item.quantity
                stock.save()

        self.status = new_status
        self.save()

    class Meta:
        verbose_name = "Orden"
        verbose_name_plural = "Órdenes"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")

    def save(self, *args, **kwargs):
        stock = Stock.objects.get(product=self.product)
        if stock.quantity < self.quantity:
            raise ValidationError(f"No hay suficiente stock para {self.product.name}.")
        stock.quantity -= self.quantity
        stock.reserved_quantity += self.quantity
        stock.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        stock = Stock.objects.get(product=self.product)
        stock.quantity += self.quantity
        stock.reserved_quantity -= self.quantity
        stock.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Orden {self.order.id})"

    class Meta:
        verbose_name = "Artículo en la orden"
        verbose_name_plural = "Artículos en la orden"