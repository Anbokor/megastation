from django.db import models
from django.db.models import Sum, F
from store.models import Product
from django.utils.timezone import now
from django.contrib.auth import get_user_model

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
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pendiente", verbose_name="Estado")

    def __str__(self):
        return f"Factura {self.invoice_number} - {self.supplier}"

    def save(self, *args, **kwargs):
        """
        ✅ Генерация номера накладной, если не задан.
        ✅ Разрешает перевод `pendiente → procesada`.
        ✅ Разрешает возврат `procesada → pendiente`.
        ✅ Блокирует любые другие изменения `procesada`.
        ✅ Блокирует любые изменения `anulada`.
        """
        if not self.invoice_number:
            self.invoice_number = f"INV-{now().strftime('%Y%m%d-%H%M%S')}"

        if not self.pk and not self.user_id:
            raise ValueError("No se puede crear una factura sin usuario.")

        if self.pk:
            old_invoice = Invoice.objects.get(pk=self.pk)

            if old_invoice.status == "procesada" and self.status == "pendiente":
                pass  # ✅ Разрешаем возврат в `pendiente` (для исправления ошибки)

            elif old_invoice.status == "procesada" and self.status != "procesada":
                raise ValueError("No se puede modificar una factura procesada.")

            elif old_invoice.status == "anulada":
                raise ValueError("No se puede modificar una factura anulada.")

        super().save(*args, **kwargs)

    @property
    def total_cost(self):
        """
        ✅ Вычисляет `total_cost`, основанный на товарах в накладной.
        """
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
        return (self.quantity or 0) * (self.cost_per_item or 0)

    class Meta:
        verbose_name = "Artículo en Factura"
        verbose_name_plural = "Artículos en Factura"
