from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "stock", "barcode", "image_preview")
    search_fields = ("name", "barcode")
    list_filter = ("category",)

    def image_preview(self, obj):
        """✅ Отображение миниатюры изображения в админке."""
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius:5px;"/>', obj.image.url)
        return format_html('<img src="/media/default_product.jpg" width="50" height="50" style="border-radius:5px;"/>')

    image_preview.short_description = "Vista previa"

