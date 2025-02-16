from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from .models import Invoice, InvoiceItem, InvoiceReturn
from store.models import Product
from inventory.models import Stock, StockMovement, SalesPoint
from orders.models import OrderItem  # ✅ Добавлена проверка проданных товаров
from django.core.exceptions import ValidationError


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ["total_cost"]
    search_fields = ["product__name"]  # ✅ Поиск по товарам в накладной


class InvoiceAdmin(admin.ModelAdmin):
    """✅ Управление накладными"""
    list_display = ["invoice_number", "supplier", "sales_point", "display_total_cost", "created_at", "status"]
    search_fields = ["invoice_number", "supplier", "items__product__name"]  # ✅ Поиск по товарам
    list_filter = ["created_at", "status", "sales_point"]
    inlines = [InvoiceItemInline]
    actions = ["process_invoices", "revert_invoice", "cancel_invoice"]

    @admin.display(description="Costo total")
    def display_total_cost(self, obj):
        return obj.total_cost if hasattr(obj, "total_cost") else "N/A"

    def update_stock(self, request, invoice):
        """✅ Обновляет склад при проведении накладной через `Stock`."""
        if not invoice.items.exists():
            messages.error(request, f"⛔ Factura {invoice.invoice_number} no tiene artículos.")
            return

        with transaction.atomic():
            stock_movements = []
            updated_stocks = []

            for item in invoice.items.all():
                stock, created = Stock.objects.get_or_create(
                    product=item.product, sales_point=invoice.sales_point, defaults={"quantity": 0}
                )
                stock.quantity += item.quantity
                updated_stocks.append(stock)

                stock_movements.append(StockMovement(
                    product=item.product, sales_point=invoice.sales_point,
                    change=item.quantity, reason=f"Recepción de factura {invoice.invoice_number}"
                ))

            if updated_stocks:
                Stock.objects.bulk_update(updated_stocks, ["quantity"])
                StockMovement.objects.bulk_create(stock_movements)
                self.log_invoice_change(request, invoice, "Factura procesada y stock actualizado")

    def revert_stock(self, request, invoice):
        """✅ Возвращает товар обратно при отмене накладной (`procesada → anulada`)."""
        if not invoice.items.exists():
            messages.warning(request, f"⚠️ La factura {invoice.invoice_number} no tiene productos para revertir.")
            return

        with transaction.atomic():
            stock_movements = []
            updated_stocks = []

            for item in invoice.items.all():
                stock = Stock.objects.filter(product=item.product, sales_point=invoice.sales_point).first()
                if not stock:
                    messages.error(request, f"⛔ No hay stock registrado para {item.product.name} en {invoice.sales_point.name}.")
                    continue

                if stock.quantity >= item.quantity:
                    stock.quantity -= item.quantity
                    updated_stocks.append(stock)

                    stock_movements.append(StockMovement(
                        product=item.product, sales_point=invoice.sales_point,
                        change=-item.quantity, reason=f"Anulación de factura {invoice.invoice_number}"
                    ))

            if updated_stocks:
                Stock.objects.bulk_update(updated_stocks, ["quantity"])
                StockMovement.objects.bulk_create(stock_movements)
                self.log_invoice_change(request, invoice, "Factura anulada y stock revertido")

    @admin.action(description=_("Procesar facturas seleccionadas y actualizar stock"))
    def process_invoices(self, request, queryset):
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status == "pendiente":
                    if not invoice.items.exists():
                        messages.error(request, f"⛔ Factura {invoice.invoice_number} no tiene artículos.")
                        continue

                    invoice.status = "procesada"
                    invoice.save()
                    self.update_stock(request, invoice)

        messages.success(request, _("✅ Facturas procesadas y stock actualizado."))

    @admin.action(description=_("Revertir facturas seleccionadas y devolver stock"))
    def revert_invoice(self, request, queryset):
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status == "procesada":
                    self.revert_stock(request, invoice)
                    invoice.status = "anulada"
                    invoice.save()

        messages.success(request, _("⚠️ Facturas revertidas y stock actualizado."))

    @admin.action(description=_("Cancelar factura"))
    def cancel_invoice(self, request, queryset):
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status == "pendiente":
                    invoice.status = "anulada"
                    invoice.save()
                    self.log_invoice_change(request, invoice, "Factura cancelada")

        messages.success(request, _("🚫 Facturas canceladas."))

    def log_invoice_change(self, request, invoice, message):
        """✅ Логирует изменения накладных в Django Admin LogEntry."""
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(invoice).id,
            object_id=invoice.id,
            object_repr=str(invoice),
            action_flag=CHANGE,
            change_message=message,
        )


admin.site.register(Invoice, InvoiceAdmin)


class InvoiceReturnAdmin(admin.ModelAdmin):
    list_display = ["invoice", "product", "sales_point", "quantity", "reason", "created_at"]
    search_fields = ["invoice__invoice_number", "product__name", "reason"]
    list_filter = ["sales_point", "created_at"]
    actions = ["cancel_return"]

    def save_model(self, request, obj, form, change):
        try:
            obj.full_clean()
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"❌ Error: {e}", level=messages.ERROR)

    @admin.action(description=_("Cancelar devolución"))
    def cancel_return(self, request, queryset):
        """✅ Запрещает удаление возврата, если товар уже продан."""
        with transaction.atomic():
            for return_entry in queryset:
                orders_with_product = OrderItem.objects.filter(product=return_entry.product).exists()
                if orders_with_product:
                    messages.error(request, f"⛔ No se puede cancelar la devolución: {return_entry.product.name} ya fue vendido.")
                    continue

                stock = Stock.objects.filter(product=return_entry.product, sales_point=return_entry.sales_point).first()
                if not stock or stock.quantity < return_entry.quantity:
                    messages.error(request, f"⛔ No hay suficiente stock para cancelar la devolución de {return_entry.product.name}.")
                    continue

                stock.quantity += return_entry.quantity
                stock.save()

                StockMovement.objects.create(
                    product=return_entry.product,
                    sales_point=return_entry.sales_point,
                    change=return_entry.quantity,
                    reason=f"Cancelación de devolución de factura {return_entry.invoice.invoice_number}"
                )

                return_entry.delete()

        messages.success(request, _("♻️ Devoluciones canceladas con éxito."))


admin.site.register(InvoiceReturn, InvoiceReturnAdmin)
