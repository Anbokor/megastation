from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Stock

class OrderItemSerializer(serializers.ModelSerializer):
    stock = serializers.SerializerMethodField()

    def get_stock(self, obj):
        """Возвращает количество товара на складе."""
        stock = Stock.objects.filter(product=obj.product).first()
        return stock.quantity if stock else 0

    def validate(self, data):
        """
        Проверяет наличие товара перед созданием `OrderItem`.
        """
        product = data['product']
        quantity = data['quantity']

        stock = Stock.objects.filter(product=product).first()
        if not stock or stock.quantity < quantity:
            raise serializers.ValidationError({"stock": f"No hay suficiente stock para {product.name}."})

        return data

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'stock']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']
        read_only_fields = ['user', 'total_price', 'created_at']

    def validate_status(self, value):
        """
        Solo los administradores pueden cambiar el estado del pedido.
        """
        request = self.context.get('request')

        if request is None:
            raise serializers.ValidationError("Falta el contexto de la solicitud.")

        if not request.user.is_staff:
            raise serializers.ValidationError("No tienes permisos para cambiar el estado del pedido.")

        return value
