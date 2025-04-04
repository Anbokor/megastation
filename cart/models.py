from django.db import models
from users.models import CustomUser
from store.models import Product

class CartItem(models.Model):
    """Model for cart items"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Usuario: {self.user.username})"

    class Meta:
        verbose_name = "Artículo en el carrito"
        verbose_name_plural = "Artículos en el carrito"
        unique_together = ("user", "product")  # Уникальность для пользователя и продукта