from rest_framework import serializers
from django.db.models import Sum
from .models import Stock, SalesPoint, StockMovement
from store.models import Product  # Correct import for Product

class SalesPointSerializer(serializers.ModelSerializer):
    """Serializer for SalesPoints"""
    class Meta:
        model = SalesPoint
        fields = ["id", "name"]

class StockSerializer(serializers.ModelSerializer):
    """Serializer for Stock"""
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")
    is_low_stock = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = ["product", "product_name", "category_name", "quantity", "low_stock_threshold", "is_low_stock"]

    def get_is_low_stock(self, obj):
        """Check if stock is below the threshold"""
        return obj.quantity < obj.low_stock_threshold

class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movements"""
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")

    def validate_change(self, value):
        """Ensure stock change is not zero"""
        if value == 0:
            raise serializers.ValidationError("El cambio en stock no puede ser cero.")
        return value

    def validate(self, data):
        """Validate that stock change doesn't result in negative quantity"""
        product = data.get("product")
        sales_point = data.get("sales_point")

        stock = Stock.objects.filter(product=product, sales_point=sales_point).first()
        if not stock:
            raise serializers.ValidationError(
                {"sales_point": "No hay stock registrado para este producto en este punto de venta."})

        if stock.quantity + data["change"] < 0:
            raise serializers.ValidationError({"change": "El stock no puede ser negativo."})

        return data

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "category_name", "sales_point", "change", "created_at", "reason"]