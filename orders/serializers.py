from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Stock

class OrderItemSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()

    def get_stock(self, obj):
        """Return available stock quantity considering reservation"""
        stock = Stock.objects.filter(product=obj.product).first()
        return stock.quantity - stock.reserved_quantity if stock else 0

    def validate(self, data):
        """Validate stock availability for immediate delivery items"""
        product = data["product"]
        quantity = data["quantity"]
        delivery_time = data.get("delivery_time", "Entrega inmediata")

        stock = Stock.objects.filter(product=product).first()

        if delivery_time == "Entrega inmediata":
            if not stock or (stock.quantity - stock.reserved_quantity) < quantity:
                raise serializers.ValidationError({"stock": f"No hay suficiente stock para {product.name} con entrega inmediata."})

        return data

    class Meta:
        model = OrderItem
        fields = ["id", "order", "product", "quantity", "stock", "delivery_time"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "created_at", "items"]
        read_only_fields = ["user", "total_price", "created_at"]

    def validate_status(self, value):
        """Allow status changes only by admins"""
        request = self.context.get("request")

        if request is None:
            raise serializers.ValidationError("Falta el contexto de la solicitud.")

        if not request.user.is_staff:
            raise serializers.ValidationError("No tienes permisos para cambiar el estado del pedido.")

        if not value:
            return self.instance.status if self.instance else "pendiente"

        return value