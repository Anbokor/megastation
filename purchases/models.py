from django.db import models
from django.db.models import Sum, F
from store.models import Product
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from inventory.models import SalesPoint, Stock, StockMovement
from orders.models import OrderItem  # ✅ Добавляем связь с заказами

User = get_user_model()


class Invoice(models.Model):
    """✅ Накладная привязана к точке продаж (`SalesPoint`)"""
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
        """✅ Контроль статусов и пересчет `total_cost`"""
        if not self.invoice_number:
            self.invoice_number = f"INV-{now().strftime('%Y%m%d-%H%M%S')}"

        if not self.pk and not self.user_id:
            raise ValidationError({"user": "No se puede crear una factura sin usuario."})

        if self.pk:
            old_invoice = Invoice.objects.get(pk=self.pk)

            if old_invoice.status == "pendiente" and self.status == "procesada":
                super().save(*args, **kwargs)
                self.update_stock()

            elif old_invoice.status == "procesada" and self.status == "anulada":
                self.revert_stock()

            elif old_invoice.status == "procesada" and self.status != "procesada":
                raise ValidationError({"status": "No se puede modificar una factura procesada."})

            elif old_invoice.status == "anulada":
                raise ValidationError({"status": "No se puede modificar una factura anulada."})

        super().save(*args, **kwargs)

    def update_stock(self):
        """✅ Добавляет товары из накладной на склад (`Stock`)."""
        stock_updates = []
        stock_movements = []

        for item in self.items.all():
            stock, created = Stock.objects.get_or_create(
                product=item.product,
                sales_point=self.sales_point,
                defaults={"quantity": 0}
            )
            stock.quantity += item.quantity
            stock_updates.append(stock)

            stock_movements.append(StockMovement(
                product=item.product,
                sales_point=self.sales_point,
                change=item.quantity,
                reason=f"Recepción de factura {self.invoice_number}"
            ))

        if stock_updates:
            Stock.objects.bulk_update(stock_updates, ["quantity"])
            StockMovement.objects.bulk_create(stock_movements)

    def revert_stock(self):
        """✅ Возвращает товары на склад при `procesada → anulada`."""
        stock_updates = []
        stock_movements = []

        for item in self.items.all():
            stock = Stock.objects.filter(product=item.product, sales_point=self.sales_point).first()
            if stock and stock.quantity >= item.quantity:
                stock.quantity -= item.quantity
                stock_updates.append(stock)

                stock_movements.append(StockMovement(
                    product=item.product,
                    sales_point=self.sales_point,
                    change=-item.quantity,
                    reason=f"Anulación de factura {self.invoice_number}"
                ))

        if stock_updates:
            Stock.objects.bulk_update(stock_updates, ["quantity"])
            StockMovement.objects.bulk_create(stock_movements)

        self.save()

    def delete(self, *args, **kwargs):
        """✅ Проверка перед удалением накладной"""
        if self.status == "procesada":
            self.revert_stock()
        super().delete(*args, **kwargs)

    @property
    def total_cost(self):
        """✅ Автоматический пересчет `total_cost`"""
        return self.items.aggregate(total=Sum(F("quantity") * F("cost_per_item")))["total"] or 0

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"


class InvoiceItem(models.Model):
    """✅ Товары в накладной"""
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Factura"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad", default=1)
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo unitario", default=0)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} en {self.invoice.invoice_number}"

    @property
    def total_cost(self):
        return (self.quantity or 0) * (self.cost_per_item or 0)

    def clean(self):
        """✅ Проверка на дублирование товаров"""
        existing_item = InvoiceItem.objects.filter(invoice=self.invoice, product=self.product).exclude(pk=self.pk).first()
        if existing_item:
            existing_item.quantity += self.quantity
            existing_item.save()
            raise ValidationError({"product": f"El producto {self.product.name} ya está en la factura, se actualizó la cantidad."})

    def save(self, *args, **kwargs):
        """✅ Автоматический пересчет `total_cost` накладной"""
        super().save(*args, **kwargs)
        self.invoice.save()

    class Meta:
        verbose_name = "Artículo en Factura"
        verbose_name_plural = "Artículos en Factura"
        ordering = ["invoice"]  # ✅ Упорядочиваем товары внутри накладной


class InvoiceReturn(models.Model):
    """✅ Возвраты товаров из накладной"""
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="returns", verbose_name="Factura")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Producto")
    sales_point = models.ForeignKey(SalesPoint, on_delete=models.CASCADE, verbose_name="Punto de venta")
    quantity = models.PositiveIntegerField(verbose_name="Cantidad")
    reason = models.CharField(max_length=255, verbose_name="Motivo del retorno")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de devolución")

    def clean(self):
        """✅ Проверяем, можно ли удалить возврат"""
        if self.invoice.status in ["anulada", "pendiente"]:
            raise ValidationError(f"No se puede devolver productos de una factura {self.invoice.status}.")

        stock = Stock.objects.filter(product=self.product, sales_point=self.sales_point).first()
        if not stock or stock.quantity < self.quantity:
            raise ValidationError({"quantity": f"No hay suficiente stock de {self.product.name} para devolver."})

    def delete(self, *args, **kwargs):
        """✅ Перед удалением проверяем, был ли товар продан после возврата"""
        orders_with_product = OrderItem.objects.filter(product=self.product).exists()
        if orders_with_product:
            raise ValidationError("No se puede eliminar el retorno: el producto ya ha sido vendido.")

        stock = Stock.objects.filter(product=self.product, sales_point=self.sales_point).first()
        if stock:
            stock.quantity += self.quantity
            stock.save()

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Devolución de {self.invoice.invoice_number})"
