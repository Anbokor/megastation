from rest_framework import serializers
from django.db.models import Sum
from .models import Product, Category
from inventory.models import Stock, StockMovement

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products"""
    availability = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=Category.objects.all(), allow_null=True)

    def get_availability(self, obj):
        """
        Get product availability status from pre-fetched data in the context
        to avoid making a database query for each product (N+1 problem).
        """
        # The stock map is pre-populated by the parent OrderSerializer.
        stock_map = self.context.get('product_stock_map', {})
        total_stock = stock_map.get(obj.id, 0)
        return "available" if total_stock > 0 else "on_order"

    def get_image_url(self, obj):
        """Get product image URL"""
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return "/static/default-product.jpg"

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "barcode", "image", "image_url", "category_id", "availability"]

class StockMovementSerializer(serializers.ModelSerializer):
    """Serializer for stock movements"""
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")

    def validate(self, data):
        """Validate stock changes"""
        product = data.get("product")
        sales_point = data.get("sales_point")
        stock = Stock.objects.filter(product=product, sales_point=sales_point).first()
        if not stock:
            raise serializers.ValidationError({"sales_point": "No hay stock registrado para este producto en este punto de venta."})
        if stock.quantity + data["change"] < 0:
            raise serializers.ValidationError({"change": "El stock не может быть отрицательным."})
        return data

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "category_name", "sales_point", "change", "created_at", "reason"]