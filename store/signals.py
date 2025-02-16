from django.db.models.signals import post_save
from django.dispatch import receiver
from store.models import Product
from inventory.models import Stock


@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    """
    Envía una alerta si el producto tiene stock bajo.
    """
    stock = Stock.objects.filter(product=instance).first()

    if stock and stock.quantity < instance.category.min_stock:
        print(f"⚠️ Alerta: El producto {instance.name} tiene stock bajo ({stock.quantity} unidades).")
