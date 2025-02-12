from django.db import models
from store.models import Product
from users.models import CustomUser

class Invoice(models.Model):
    """
    Factura de compra de productos.
    """
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Número de factura")  # 🔥 Новый параметр
    supplier = models.CharField(max_length=255, verbose_name="Proveedor")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="Usuario")  # 🔥 Кто завёл накладную

    def __str__(self):
        return f"Factura {self.invoice_number} de {self.supplier}"


class InvoiceItem(models.Model):
    """
    Productos comprados dentro de una factura.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items", verbose_name="Factura")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de compra")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en Factura {self.invoice.id}"
