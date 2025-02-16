from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category
from django_celery_beat.models import (
    PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule
)
from inventory.models import Stock
from django_celery_beat.admin import PeriodicTaskAdmin as DefaultPeriodicTaskAdmin

# ✅ Удаляем Celery Tasks из корня админки
celery_models = [PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule]

for model in celery_models:
    if admin.site.is_registered(model):
        admin.site.unregister(model)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "get_stock", "barcode", "image_preview")
    search_fields = ("name", "barcode")
    list_filter = ("category",)

    def get_queryset(self, request):
        """
        ✅ Предзагружаем `Stock` одним SQL-запросом (чтобы избежать N+1 запросов).
        """
        return super().get_queryset(request).prefetch_related("stock_info")

    def get_stock(self, obj):
        """
        ✅ Оптимизированное получение `Stock.quantity` (из загруженных данных).
        """
        stock = obj.stock_info.first()  # ✅ Берем первый складской остаток
        return stock.quantity if stock else "Sin stock"

    get_stock.short_description = "Stock disponible"

    def image_preview(self, obj):
        """
        ✅ Отображение миниатюры изображения в админке.
        """
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.image.url)
        return format_html('<img src="/media/default_product.jpg" width="50" height="50" style="border-radius:5px;"/>')

    image_preview.short_description = "Vista previa"
