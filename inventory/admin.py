from django.contrib import admin
from .models import Stock, StockMovement, SalesPoint
from store.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class SalesPointAdmin(admin.ModelAdmin):
    """✅ Управление точками продаж в админке."""
    list_display = ["name", "get_administrators", "get_sellers"]
    search_fields = ["name"]
    filter_horizontal = ["administrators", "sellers"]

    @admin.display(description="Administradores")
    def get_administrators(self, obj):
        """✅ Показывает всех администраторов точки продаж."""
        return ", ".join([user.username for user in obj.administrators.all()])

    @admin.display(description="Vendedores")
    def get_sellers(self, obj):
        """✅ Показывает всех продавцов точки продаж."""
        return ", ".join([user.username for user in obj.sellers.all()])

admin.site.register(SalesPoint, SalesPointAdmin)

class StockAdmin(admin.ModelAdmin):
    """✅ Управление остатками товаров на складах в разных точках продаж."""
    list_display = ["product", "sales_point", "category", "quantity", "low_stock_threshold", "is_low_stock"]
    search_fields = ["product__name", "product__category__name", "sales_point__name"]
    list_filter = ["product__category", "sales_point"]

    @admin.display(description="Categoría")
    def category(self, obj):
        """✅ Отображает категорию продукта."""
        return obj.product.category.name if obj.product.category else "Sin categoría"

    @admin.display(description="Punto de venta")
    def sales_point(self, obj):
        """✅ Показывает точку продаж."""
        return obj.sales_point.name

    @admin.display(description="Stock bajo", boolean=True)
    def is_low_stock(self, obj):
        """✅ Показывает, находится ли товар в низком запасе."""
        return obj.quantity <= obj.low_stock_threshold

admin.site.register(Stock, StockAdmin)

class StockMovementAdmin(admin.ModelAdmin):
    """✅ Управление перемещениями товаров между складами."""
    list_display = ["product", "sales_point", "category", "change", "created_at", "reason"]
    search_fields = ["product__name", "product__category__name", "sales_point__name", "reason"]
    list_filter = ["created_at", "product__category", "sales_point"]
    date_hierarchy = "created_at"

    @admin.display(description="Categoría")
    def category(self, obj):
        """✅ Отображает категорию продукта."""
        return obj.product.category.name if obj.product.category else "Sin categoría"

    @admin.display(description="Punto de venta")
    def sales_point(self, obj):
        """✅ Показывает точку продаж."""
        return obj.sales_point.name

admin.site.register(StockMovement, StockMovementAdmin)
