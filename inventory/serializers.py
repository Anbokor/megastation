from rest_framework import serializers
from .models import Stock, SalesPoint, StockMovement


class SalesPointSerializer(serializers.ModelSerializer):
    """✅ Сериализатор точки продаж"""

    class Meta:
        model = SalesPoint
        fields = ["id", "name"]


class StockSerializer(serializers.ModelSerializer):
    """✅ Сериализатор склада"""
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ["product", "product_name", "category_name", "quantity", "low_stock_threshold", "is_low_stock"]

    def get_is_low_stock(self, obj):
        return obj.quantity < obj.low_stock_threshold


class StockMovementSerializer(serializers.ModelSerializer):
    """✅ Сериализатор движений товара на складе"""
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "category_name", "sales_point", "change", "created_at", "reason"]

    def validate_change(self, value):
        if value == 0:
            raise serializers.ValidationError("El cambio en stock no puede ser cero.")
        return value

    def validate(self, data):
        """✅ Проверяем, что изменение `change` не сделает `Stock.quantity` отрицательным."""
        product = data.get("product")
        sales_point = data.get("sales_point")

        stock = Stock.objects.filter(product=product, sales_point=sales_point).first()
        if not stock:
            raise serializers.ValidationError(
                {"sales_point": "No hay stock registrado para este producto en este punto de venta."})

        if stock.quantity + data["change"] < 0:
            raise serializers.ValidationError({"change": "El stock no puede ser negativo."})

        return data
