from django.contrib import admin, messages
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Invoice, InvoiceItem, InvoiceReturn
from inventory.models import Stock, StockMovement


class InvoiceItemInline(admin.TabularInline):
    """ ✅ Только для отображения товаров в фактуре (без редактирования) """
    model = InvoiceItem
    extra = 0
    readonly_fields = ("product", "quantity", "cost_per_item", "total_cost")

    def total_cost(self, obj):
        return obj.quantity * obj.cost_per_item


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """ ✅ Улучшенный интерфейс управления фактурами """
    list_display = ("invoice_number", "supplier", "sales_point", "display_total_cost", "created_at", "status", "view_items_link")
    search_fields = ("invoice_number", "supplier")
    list_filter = ("created_at", "status", "sales_point")
    readonly_fields = ("created_at", "display_items", "display_total_cost")
    actions = ["procesar_factura", "anular_factura"]

    def display_total_cost(self, obj):
        """ ✅ Показывает общую сумму товаров в фактуре """
        return obj.total_cost
    display_total_cost.short_description = "Costo total"

    def display_items(self, obj):
        """ ✅ Показывает товары в фактуре в удобном виде """
        items = obj.items.all()
        if not items:
            return "No hay productos en esta factura"
        html = "<ul>"
        for item in items:
            html += f"<li>{item.quantity} x {item.product.name} - ${item.cost_per_item}</li>"
        html += "</ul>"
        return mark_safe(html)
    display_items.short_description = "Productos en la factura"

    def view_items_link(self, obj):
        """ ✅ Ссылка на редактирование товаров этой фактуры """
        url = reverse("admin:purchases_invoiceitem_changelist") + f"?invoice__id__exact={obj.id}"
        return mark_safe(f'<a href="{url}">Ver artículos</a>')
    view_items_link.short_description = "Editar artículos"

    def procesar_factura(self, request, queryset):
        """ ✅ Обновляет статус фактуры и пересчитывает складской остаток """
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status != "pendiente":
                    self.message_user(request, f"❌ Factura {invoice.invoice_number} ya ha sido procesada o anulada.", messages.ERROR)
                    continue

                if not invoice.items.exists():
                    self.message_user(request, f"⚠️ Factura {invoice.invoice_number} no tiene artículos.", messages.WARNING)
                    continue

                for item in invoice.items.all():
                    stock, _ = Stock.objects.get_or_create(product=item.product, sales_point=invoice.sales_point, defaults={"quantity": 0})
                    stock.quantity += item.quantity
                    stock.save()

                    StockMovement.objects.create(
                        product=item.product,
                        sales_point=invoice.sales_point,
                        change=item.quantity,
                        reason=f"Recepción de factura {invoice.invoice_number}"
                    )

                invoice.status = "procesada"
                invoice.save()
                self.message_user(request, f"✅ Factura {invoice.invoice_number} procesada correctamente.", messages.SUCCESS)
    procesar_factura.short_description = "Procesar facturas seleccionadas"

    def anular_factura(self, request, queryset):
        """ ✅ Отменяет фактуру и откатывает складские изменения """
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status != "procesada":
                    self.message_user(request, f"❌ Factura {invoice.invoice_number} no se puede anular porque no ha sido procesada.", messages.ERROR)
                    continue

                for item in invoice.items.all():
                    stock = Stock.objects.filter(product=item.product, sales_point=invoice.sales_point).first()
                    if not stock or stock.quantity < item.quantity:
                        self.message_user(request, f"⚠️ No hay suficiente stock para anular {item.product.name}.", messages.WARNING)
                        continue

                    stock.quantity -= item.quantity
                    stock.save()

                    StockMovement.objects.create(
                        product=item.product,
                        sales_point=invoice.sales_point,
                        change=-item.quantity,
                        reason=f"Anulación de factura {invoice.invoice_number}"
                    )

                invoice.status = "anulada"
                invoice.save()
                self.message_user(request, f"✅ Factura {invoice.invoice_number} anulada correctamente.", messages.SUCCESS)
    anular_factura.short_description = "Anular facturas seleccionadas"


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """ ✅ Отдельный интерфейс для управления товарами в фактурах """
    list_display = ("invoice", "product", "quantity", "cost_per_item", "total_cost")
    search_fields = ("invoice__invoice_number", "product__name")
    list_filter = ("invoice__created_at",)
    readonly_fields = ("total_cost",)

    def total_cost(self, obj):
        return obj.quantity * obj.cost_per_item
    total_cost.short_description = "Costo total"


@admin.register(InvoiceReturn)
class InvoiceReturnAdmin(admin.ModelAdmin):
    """ ✅ Управление возвратами товаров """
    list_display = ("invoice", "product", "sales_point", "quantity", "reason", "created_at")
    search_fields = ("invoice__invoice_number", "product__name")
    list_filter = ("sales_point", "created_at")
