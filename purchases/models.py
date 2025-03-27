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

        with transaction.atomic():
            super().save(*args, **kwargs)

    def update_stock(self):
        if not self.items.exists():
            raise ValidationError("No se puede procesar una factura sin artículos.")
        with transaction.atomic():
            for item in self.items.all():
                stock, created = Stock.objects.get_or_create(
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
                total_returned = self.returns.filter(product=item.product).aggregate(Sum('quantity'))['quantity__sum'] or 0
                remaining_quantity = item.quantity - total_returned
                if not stock or stock.quantity < remaining_quantity:
                    raise ValidationError(f"No hay suficiente stock para revertir {item.product.name}.")
                stock.quantity -= remaining_quantity
                stock.save()
                StockMovement.objects.create(
                    product=item.product,
                    sales_point=self.sales_point,
                    change=-remaining_quantity,
                    reason=f"Anulación de factura {self.invoice_number}"
                )

    def delete(self, *args, **kwargs):
        with transaction.atomic():
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
            is_new = self._state.adding
            if not is_new:
                old_instance = InvoiceItem.objects.get(pk=self.pk)
                quantity_diff = self.quantity - old_instance.quantity
                if quantity_diff != 0 and self.invoice.status == "procesada":
                    stock = Stock.objects.filter(product=self.product, sales_point=self.invoice.sales_point).first()
                    if stock:
                        if quantity_diff > 0:
                            stock.quantity += quantity_diff
                        elif stock.quantity >= -quantity_diff:
                            stock.quantity -= -quantity_diff
                        else:
                            raise ValidationError(f"No hay suficiente stock para reducir {self.product.name}.")
                        stock.save()
                        StockMovement.objects.create(
                            product=self.product,
                            sales_point=self.invoice.sales_point,
                            change=quantity_diff,
                            reason=f"Modificación de factura {self.invoice.invoice_number}"
                        )

            existing_item = InvoiceItem.objects.filter(
                invoice=self.invoice, product=self.product
            ).exclude(pk=self.pk).first()
            if existing_item:
                existing_item.quantity += self.quantity
                existing_item.save()
                return
            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if self.invoice.status == "procesada":
                stock = Stock.objects.filter(product=self.product, sales_point=self.invoice.sales_point).first()
                if stock and stock.quantity >= self.quantity:
                    stock.quantity -= self.quantity
                    stock.save()
                    StockMovement.objects.create(
                        product=self.product,
                        sales_point=self.invoice.sales_point,
                        change=-self.quantity,
                        reason=f"Eliminación de artículo de factura {self.invoice.invoice_number}"
                    )
                else:
                    raise ValidationError(f"No hay suficiente stock para eliminar {self.product.name}.")
            super().delete(*args, **kwargs)

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
        invoice_item = InvoiceItem.objects.filter(invoice=self.invoice, product=self.product).first()
        if not invoice_item:
            raise ValidationError({"product": f"El producto {self.product.name} no está en la factura."})
        total_returned = self.invoice.returns.filter(product=self.product).exclude(id=self.id).aggregate(Sum('quantity'))['quantity__sum'] or 0
        available_to_return = invoice_item.quantity - total_returned
        if not stock or stock.quantity < self.quantity:
            raise ValidationError({"quantity": f"No hay suficiente stock de {self.product.name} para devolver."})
        if self.quantity > available_to_return:
            raise ValidationError({"quantity": f"No se puede devolver más de {available_to_return} unidades de {self.product.name}."})

    def save(self, *args, **kwargs):
        with transaction.atomic():
            self.clean()
            is_new = self._state.adding
            stock = Stock.objects.filter(product=self.product, sales_point=self.sales_point).first()
            if not is_new:
                old_instance = InvoiceReturn.objects.get(pk=self.pk)
                quantity_diff = self.quantity - old_instance.quantity
                if quantity_diff != 0:
                    if quantity_diff > 0 and stock.quantity >= quantity_diff:
                        stock.quantity -= quantity_diff
                        stock.save()
                        StockMovement.objects.create(
                            product=self.product,
                            sales_point=self.sales_point,
                            change=-quantity_diff,
                            reason=f"Modificación de devolución de factura {self.invoice.invoice_number}"
                        )
                    elif quantity_diff < 0:
                        stock.quantity += abs(quantity_diff)
                        stock.save()
                        StockMovement.objects.create(
                            product=self.product,
                            sales_point=self.sales_point,
                            change=abs(quantity_diff),
                            reason=f"Modificación de devolución de factura {self.invoice.invoice_number}"
                        )
            else:
                if stock.quantity >= self.quantity:
                    stock.quantity -= self.quantity
                    stock.save()
                    StockMovement.objects.create(
                        product=self.product,
                        sales_point=self.sales_point,
                        change=-self.quantity,
                        reason=f"Devolución de factura {self.invoice.invoice_number}"
                    )
                else:
                    raise ValidationError(f"No hay suficiente stock de {self.product.name} para devolver.")

            super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if OrderItem.objects.filter(product=self.product).exists():
                raise ValidationError("No se puede eliminar el retorno: el producto ya ha sido vendido.")
            stock = Stock.objects.filter(product=self.product, sales_point=self.sales_point).first()
            if stock:
                stock.quantity += self.quantity
                stock.save()
                StockMovement.objects.create(
                    product=self.product,
                    sales_point=self.sales_point,
                    change=self.quantity,
                    reason=f"Cancelación de devolución de factura {self.invoice.invoice_number}"
                )
            super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Devolución de {self.invoice.invoice_number})"