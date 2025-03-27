from django.contrib import admin, messages
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Invoice, InvoiceItem, InvoiceReturn
from inventory.models import Stock, StockMovement

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ('product', 'quantity', 'cost_per_item', 'total_cost')
    readonly_fields = ('total_cost',)
    autocomplete_fields = ['product']

    def total_cost(self, obj):
        return obj.total_cost if obj.quantity and obj.cost_per_item else 0
    total_cost.short_description = "Costo total"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'sales_point', 'display_total_cost', 'created_at', 'status')
    list_filter = ('status', 'sales_point', 'created_at')
    search_fields = ('invoice_number', 'supplier')
    inlines = [InvoiceItemInline]
    fieldsets = (
        (None, {
            'fields': ('invoice_number', 'supplier', 'sales_point', 'status')
        }),
        ('Detalles', {
            'fields': ('created_at', 'display_total_cost'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'display_total_cost')

    def display_total_cost(self, obj):
        return obj.total_cost
    display_total_cost.short_description = "Costo total"

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        with transaction.atomic():
            super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        with transaction.atomic():
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk:
                    instance.invoice = form.instance
                instance.save()
            formset.save_m2m()
            if form.instance.status == "procesada" and instances:
                try:
                    form.instance.update_stock()
                except ValidationError as e:
                    messages.error(request, str(e))
            elif form.instance.status == "procesada" and not instances:
                messages.warning(request, "Factura procesada sin artículos no actualiza el stock.")

    def delete_model(self, request, obj):
        try:
            with transaction.atomic():
                obj.delete()
            messages.success(request, f"Factura {obj.invoice_number} eliminada correctamente.")
        except ValidationError as e:
            messages.error(request, str(e))

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'procesada':
            return ['invoice_number', 'supplier', 'sales_point', 'status', 'created_at', 'display_total_cost']
        return ['created_at', 'display_total_cost']

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'quantity', 'cost_per_item', 'total_cost')
    search_fields = ('invoice__invoice_number', 'product__name')
    list_filter = ('invoice__created_at',)
    readonly_fields = ('total_cost',)

    def total_cost(self, obj):
        return obj.total_cost
    total_cost.short_description = "Costo total"

@admin.register(InvoiceReturn)
class InvoiceReturnAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'sales_point', 'quantity', 'reason', 'created_at')
    search_fields = ('invoice__invoice_number', 'product__name')
    list_filter = ('sales_point', 'created_at')
    autocomplete_fields = ['product', 'sales_point']

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
            messages.success(request, "Retorno guardado correctamente.")
        except ValidationError as e:
            messages.error(request, str(e))