from rest_framework import serializers
from .models import Product, Category
from inventory.models import Stock, StockMovement

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProductSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()  # ✅ Добавляем `image_url` как отдельное поле

    def get_stock(self, obj):
        """✅ Возвращает количество товара со склада."""
        stock = Stock.objects.filter(product=obj).first()
        return stock.quantity if stock else 0

    def get_image_url(self, obj):
        """✅ Возвращает полный URL изображения, если оно есть."""
        request = self.context.get("request")
        if obj.image:
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None  # ✅ Теперь возвращает `None`, если изображения нет

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "stock", "barcode", "image", "image_url"]

class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    category_name = serializers.ReadOnlyField(source="product.category.name")

    def validate(self, data):
        """
        ✅ Проверяем, что изменение `change` не приведёт к отрицательному `Stock.quantity`.
        """
        product = data.get("product")
        sales_point = data.get("sales_point")

        # ✅ Проверяем, существует ли складская запись для товара в этой точке продаж
        stock = Stock.objects.filter(product=product, sales_point=sales_point).first()
        if not stock:
            raise serializers.ValidationError({"sales_point": "No hay stock registrado para este producto en este punto de venta."})

        # ✅ Проверяем, не уходит ли запас в минус
        if stock.quantity + data["change"] < 0:
            raise serializers.ValidationError({"change": "El stock no puede ser negativo."})

        return data

    class Meta:
        model = StockMovement
        fields = ["id", "product", "product_name", "category_name", "sales_point", "change", "created_at", "reason"]