from django.db import models
from users.models import CustomUser
from store.models import Product
from inventory.models import Stock  # Импортируем склад


class CartItem(models.Model):
    """
    ✅ Модель элемента корзины. Добавлена логика проверки наличия товара на складе,
    но резервирование теперь происходит только при оформлении заказа.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cart")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        """
        ✅ Проверка наличия товара на складе перед добавлением в корзину.
        Однако резервирование товара теперь происходит только при оплате заказа.
        """
        stock = Stock.objects.filter(product=self.product).first()

        if not stock or stock.quantity < self.quantity:
            raise ValueError(f"No hay suficiente stock para {self.product.name}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Usuario: {self.user.username})"

    class Meta:
        verbose_name = "Artículo en el carrito"
        verbose_name_plural = "Artículos en el carrito"
