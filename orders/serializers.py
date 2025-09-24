from rest_framework import serializers
from django.db.models import Sum, F
from .models import Order, OrderItem
from users.serializers import SimpleUserSerializer
from store.serializers import ProductSerializer
from inventory.models import Stock

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "product", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = SimpleUserSerializer(read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    def to_representation(self, instance):
        """
        This is the final fix. The previous approach of using context failed because
        the context was not being passed down to the nested ProductSerializer.
        
        This new approach manually injects the availability data after the default
        serialization is complete. It's a more robust and direct method.
        """
        # 1. Get the default serialized data.
        data = super().to_representation(instance)
        
        # 2. Calculate the available stock, just like before.
        product_ids = [item['product']['id'] for item in data['items']]
        
        stocks = Stock.objects.filter(product_id__in=product_ids)\
            .values('product_id')\
            .annotate(available_stock=Sum(F('quantity') - F('reserved_quantity')))
            
        stock_map = {s['product_id']: s['available_stock'] for s in stocks}
        
        # 3. Manually iterate and inject the availability into the serialized data.
        for item_data in data['items']:
            product_id = item_data['product']['id']
            available_stock = stock_map.get(product_id, 0)
            item_data['product']['availability'] = "available" if available_stock > 0 else "on_order"
            
        # 4. Return the modified data.
        return data

    class Meta:
        model = Order
        fields = [
            "id", "user", "status", "status_display", "total_price", 
            "created_at", "items", "payment_method", "payment_method_display"
        ]
        read_only_fields = ["user", "total_price", "created_at"]
