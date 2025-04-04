from rest_framework import serializers
from .models import CartItem
from store.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'quantity']