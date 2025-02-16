from rest_framework import serializers
from .models import Stock, StockMovement
from .models import SalesPoint
from django.contrib.auth import get_user_model

User = get_user_model()

class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name", read_only=True)
    category_name = serializers.CharField(source="product.category.name", read_only=True)
    is_low_stock = serializers.SerializerMethodField()

    def get_is_low_stock(self, obj):
        """✅ Проверяет, находится ли запас товара ниже порога."""
        return obj.quantity <= obj.low_stock_threshold

    class Meta:
        model = Stock
        fields = ["product", "product_name", "category_name", "quantity", "low_stock_threshold", "is_low_stock"]

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "category_name", "change", "created_at", "reason"]

class SalesPointSerializer(serializers.ModelSerializer):
    administrators = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(is_staff=True))
    sellers = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(is_staff=False))

    class Meta:
        model = SalesPoint
        fields = ["id", "name", "administrators", "sellers"]