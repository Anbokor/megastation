from rest_framework import serializers
from .models import Product, Category
from .models import StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'price', 'stock', 'barcode']

class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = '__all__'  # ✅ Теперь API вернёт все поля
