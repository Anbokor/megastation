from django.db import models, transaction
from django.db.models import Sum, F
from store.models import Product
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from inventory.models import SalesPoint, Stock, StockMovement
from orders.models import OrderItem

User = get_user_model()


class Invoice(models.Model):
    STATUS_CHOICES = [
        ("pendiente", "Pendiente"),
        ("procesada", "Procesada"),
        ("anulada", "Anulada"),
    ]

    invoice_number = models.CharField(max_length=20, unique=True, blank=True, verbose_name="Número de factura")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    supplier = models.CharField(max_length=100, verbose_name="Proveedor")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    sales_point = models.ForeignKey(SalesPoint, on_delete=models.CASCADE, related_name="invoices", verbose_name="Punto de venta")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pendiente", verbose_name="Estado")

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.supplier}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if not self.invoice_number:
            self.invoice_number = f"INV-{now().strftime('%Y%m%d-%H%M%S')}"

        if is_new and not self.user_id:
            raise ValidationError({"user": "No se puede crear una factura sin usuario."})

        if not is_new:
            old_invoice = Invoice.objects.get(pk=self.pk)
            with transaction.atomic():
                if old_invoice.status == "pendiente" and self.status == "procesada":
                    self.update_stock()
                elif old_invoice.status == "procesada" and self.status == "anulada":
                    self.revert_stock()
                elif old_invoice.status == "procesada" and self.status not in ["procesada", "anulada"]:
                    raise ValidationError({"status": "No se puede modificar una factura procesada."})
        super().save(*args, **kwargs)

    def update_stock(self):
        if not self.items.exists():
            raise ValidationError("No se puede procesar una factura sin artículos.")
        with transaction.atomic():
            for item in self.items.all():
                stock, _ = Stock.objects.get_or_create(
                    product=item.product, sales_point=self.sales_point, defaults={"quantity": 0}
                )
                stock.quantity += item.quantity
                stock.save()

                StockMovement.objects.create(
                    product=item.product,
                    sales_point=self.sales_point,
                    change=item.quantity,
                    reason=f"Recepción de factura {self.invoice_number}"
                )

    def revert_stock(self):
        if not self.items.exists():
            raise ValidationError("No se puede revertir una factura sin artículos.")
        with transaction.atomic():
            for item in self.items.all():
                stock = Stock.objects.filter(product=item.product, sales_point=self.sales_point).first()
                if not stock or stock.quantity < item.quantity:
                    raise ValidationError(f"No hay suficiente stock para revertir {item.product.name}.")
                stock.quantity -= item.quantity
                stock.save()

                StockMovement.objects.create(
                    product=item.product,
                    sales_point=self.sales_point,
                    change=-item.quantity,
                    reason=f"Anulación de factura {self.invoice_number}"
                )

    def delete(self, *args, **kwargs):
        if self.status == "procesada":
            self.revert_stock()
        super().delete(*args, **kwargs)

    @property
    def total_cost(self):
        return self.items.aggregate(total=Sum(F("quantity") * F("cost_per_item")))["total"] or 0

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items", verbose_name="Factura")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", default=1)
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo unitario", default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.invoice.invoice_number}"

    @property
    def total_cost(self):
        return self.quantity * self.cost_per_item

    def save(self, *args, **kwargs):
        with transaction.atomic():
            existing_item = InvoiceItem.objects.filter(
                invoice=self.invoice, product=self.product
            ).exclude(pk=self.pk).first()
            if existing_item:
                existing_item.quantity += self.quantity
                existing_item.save()
                return
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Artículo en Factura"
        verbose_name_plural = "Artículos en Factura"
        ordering = ["invoice"]


class InvoiceReturn(models.Model):
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="returns", verbose_name="Factura")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    sales_point = models.ForeignKey(SalesPoint, on_delete=models.CASCADE, verbose_name="Punto de venta")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    reason = models.CharField(max_length=255, verbose_name="Motivo del retorno")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de devolución")

    def clean(self):
        if self.invoice.status in ["anulada", "pendiente"]:
            raise ValidationError(f"No se puede devolver productos de una factura {self.invoice.status}.")
        stock = Stock.objects.filter(product=self.product, sales_point=self.sales_point).first()
        if not stock or stock.quantity < self.quantity:
            raise ValidationError({"quantity": f"No hay suficiente stock de {self.product.name} para devolver."})

    def delete(self, *args, **kwargs):
        if OrderItem.objects.filter(product=self.product).exists():
            raise ValidationError("No se puede eliminar el retorno: el producto ya ha sido vendido.")
        with transaction.atomic():
            stock = Stock.objects.filter(product=self.product, sales_point=self.sales_point).first()
            if stock:
                stock.quantity += self.quantity
                stock.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Devolución de {self.invoice.invoice_number})"
