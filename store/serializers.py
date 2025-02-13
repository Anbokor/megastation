from rest_framework import serializers
from .models import Product, Category, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # ✅ Добавлена категория
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "barcode", "image_url", "category"]

    def get_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return request.build_absolute_uri("/media/default_product.jpg") if request else "/media/default_product.jpg"


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")  # ✅ Показываем имя товара в API

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "change", "created_at", "reason"]
