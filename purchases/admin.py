from django.contrib import admin
from .models import Invoice, InvoiceItem

class InvoiceItemInline(admin.TabularInline):
    """
    Позволяет редактировать позиции накладной прямо в админке.
    """
    model = InvoiceItem
    extra = 1  # 🔥 Показывает пустую строку для добавления новых позиций

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """
    Настройка админки для накладных.
    """
    list_display = ("invoice_number", "supplier", "user", "created_at")  # 🔥 Поля в списке
    search_fields = ("invoice_number", "supplier")  # 🔍 Поиск по номеру и поставщику
    list_filter = ("created_at", "supplier")  # 📅 Фильтр по дате и поставщику
    inlines = [InvoiceItemInline]  # 🔥 Позволяет редактировать позиции накладной

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """
    Настройка админки для позиций накладных.
    """
    list_display = ("invoice", "product", "quantity", "purchase_price")  # 🔥 Поля в списке
    search_fields = ("product__name", "invoice__invoice_number")  # 🔍 Поиск по продукту и накладной
