from rest_framework import serializers
from .models import Product, Category
from inventory.models import Stock, StockMovement

class CategorySerializer(serializers.ModelSerializer):
    """✅ Сериализатор для категорий"""
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProductSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=Category.objects.all(), allow_null=True)

    def get_stock(self, obj):
        stock = Stock.objects.filter(product=obj).first()
        return stock.quantity if stock else 0

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return "/static/default-product.jpg"

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "barcode", "image", "image_url", "category_id"]

class StockMovementSerializer(serializers.ModelSerializer):
    """✅ Сериализатор для движения товаров на складе"""
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")

    def validate(self, data):
        product = data.get("product")
        sales_point = data.get("sales_point")
        stock = Stock.objects.filter(product=product, sales_point=sales_point).first()
        if not stock:
            raise serializers.ValidationError({"sales_point": "No hay stock registrado para este producto en este punto de venta."})
        if stock.quantity + data["change"] < 0:
            raise serializers.ValidationError({"change": "El stock no puede ser negativo."})
        return data

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "category_name", "sales_point", "change", "created_at", "reason"]