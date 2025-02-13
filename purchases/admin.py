from django.contrib import admin, messages
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.auth.models import Group
from .models import Invoice, InvoiceItem
from store.models import Product, StockMovement


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0  # 🔥 Отключает автоматическое добавление пустых строк
    readonly_fields = ["total_cost"]


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "supplier", "get_total_cost", "created_at", "status"]
    search_fields = ["invoice_number", "supplier"]
    list_filter = ["created_at", "status"]
    inlines = [InvoiceItemInline]
    actions = ["process_invoices", "revert_invoice"]

    def has_module_permission(self, request):
        """✅ Только администраторы и продавцы могут видеть раздел Invoices"""
        return request.user.is_superuser or request.user.groups.filter(name__in=["Administradores", "Vendedores"]).exists()

    def has_view_permission(self, request, obj=None):
        """✅ Только администраторы и продавцы могут просматривать накладные"""
        return self.has_module_permission(request)

    def has_add_permission(self, request):
        """✅ Только администраторы и продавцы могут добавлять накладные"""
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None):
        """✅ Только администраторы и продавцы могут изменять накладные"""
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None):
        """✅ Запрещаем удалять проведенные накладные"""
        if obj and obj.status == "procesada":
            return False
        return self.has_module_permission(request)

    def save_model(self, request, obj, form, change):
        """
        ✅ Логика сохранения накладной:
        - Генерирует `invoice_number`, если пустой.
        - Автоматически подставляет `user`, если пустой.
        - Разрешает `pendiente → procesada` (увеличивает склад).
        - Разрешает `procesada → pendiente` (уменьшает склад).
        - Разрешает `procesada → anulada` (уменьшает склад).
        - Запрещает любые изменения `anulada`, кроме удаления.
        """
        if not obj.invoice_number:
            obj.invoice_number = f"INV-{now().strftime('%Y%m%d-%H%M%S')}"

        if not obj.user_id:
            obj.user = request.user

        if change:
            old_invoice = Invoice.objects.get(pk=obj.pk)

            if old_invoice.status == "anulada":
                messages.error(request, "⛔ No se puede modificar una factura anulada.")
                return

            if old_invoice.status == "procesada" and obj.status == "pendiente":
                self.revert_stock(request, obj)  # ✅ Возвращаем товары обратно на склад
                messages.success(request, f"✅ Factura {obj.invoice_number} revertida a 'pendiente'. Stock actualizado.")

            elif old_invoice.status == "pendiente" and obj.status == "procesada":
                if not obj.items.exists():
                    messages.error(request, f"⛔ Factura {obj.invoice_number} no tiene artículos.")
                    return
                self.update_stock(request, obj)  # ✅ Добавляем товары на склад
                messages.success(request, f"✅ Factura {obj.invoice_number} procesada. Stock actualizado.")

            elif old_invoice.status == "procesada" and obj.status == "anulada":
                self.revert_stock(request, obj)  # ✅ Убираем товары со склада при аннулировании
                messages.warning(request, f"⚠️ Factura {obj.invoice_number} anulada. Stock reducido.")

        super().save_model(request, obj, form, change)

    def get_total_cost(self, obj):
        """✅ Вычисляет `total_cost` для списка накладных."""
        return obj.total_cost
    get_total_cost.short_description = "Costo total"

    def update_stock(self, request, invoice):
        """
        ✅ Обновляет склад при проведении накладной.
        """
        if not invoice.items.exists():
            messages.error(request, f"⛔ Factura {invoice.invoice_number} no tiene artículos.")
            return

        with transaction.atomic():
            stock_movements = []
            updated_products = []

            for item in invoice.items.all():
                item.product.stock += item.quantity  # ✅ Добавляем товар на склад
                updated_products.append(item.product)

                stock_movements.append(
                    StockMovement(
                        product=item.product,
                        change=item.quantity,
                        reason=f"Recepción de factura {invoice.invoice_number}",
                    )
                )

            if updated_products:
                Product.objects.bulk_update(updated_products, ["stock"])
                StockMovement.objects.bulk_create(stock_movements)

    def revert_stock(self, request, invoice):
        """
        ✅ Возвращает товар обратно при отмене накладной или откате `procesada → pendiente` или `procesada → anulada`.
        """
        if not invoice.items.exists():
            messages.warning(request, f"⚠️ La factura {invoice.invoice_number} no tiene productos para revertir.")
            return

        with transaction.atomic():
            stock_movements = []
            updated_products = []

            for item in invoice.items.all():
                if item.product.stock >= item.quantity:
                    item.product.stock -= item.quantity  # ✅ Уменьшаем stock
                    updated_products.append(item.product)

                    stock_movements.append(
                        StockMovement(
                            product=item.product,
                            change=-item.quantity,
                            reason=f"Anulación de factura {invoice.invoice_number}",
                        )
                    )

            if updated_products:
                Product.objects.bulk_update(updated_products, ["stock"])
                StockMovement.objects.bulk_create(stock_movements)

    @admin.action(description=_("Procesar facturas seleccionadas y actualizar stock"))
    def process_invoices(self, request, queryset):
        """
        ✅ Массовая обработка накладных (изменение `pendiente` → `procesada`).
        """
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status == "pendiente":
                    if not invoice.items.exists():
                        messages.error(request, f"⛔ Factura {invoice.invoice_number} no tiene artículos.")
                        continue
                    self.update_stock(request, invoice)
                    invoice.status = "procesada"
                    invoice.save()
        messages.success(request, _("✅ Facturas procesadas y stock actualizado."))

    @admin.action(description=_("Revertir facturas seleccionadas y devolver stock"))
    def revert_invoice(self, request, queryset):
        """
        ✅ Отменяет накладные и возвращает товар обратно (`procesada` → `anulada`).
        """
        with transaction.atomic():
            for invoice in queryset:
                if invoice.status == "procesada":
                    self.revert_stock(request, invoice)
                    invoice.status = "anulada"
                    invoice.save()
        messages.success(request, _("⚠️ Facturas revertidas y stock actualizado."))


admin.site.register(Invoice, InvoiceAdmin)
