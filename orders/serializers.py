from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'created_at', 'items']
        read_only_fields = ['user', 'total_price', 'created_at']

    def validate_status(self, value):
        """
        Only administrators can change the order status.
        """
        request = self.context.get('request')


        if request is None:
            raise serializers.ValidationError("Request context is missing.")

        if not request.user.is_staff:
            raise serializers.ValidationError("No tienes permisos para cambiar el estado del pedido.")

        return value
