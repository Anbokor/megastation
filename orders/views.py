from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from store.models import Product
from users.permissions import CanAdvanceOrderStatus
from inventory.models import Stock, StockMovement
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .utils import send_order_status_email
from django.db import transaction

class OrderListView(generics.ListCreateAPIView):
    """API to list and create orders"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Create order without immediate reservation"""
        serializer.save(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """API to retrieve, update, and delete orders"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        """Update order with reservation logic"""
        instance = serializer.instance
        old_status = instance.status
        new_status = self.request.data.get("status", old_status)

        if old_status != new_status:
            instance.update_status(new_status)

        serializer.save()

class OrderCreateView(generics.CreateAPIView):
    """Create order from cart with delivery times"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = request.data.get("items", [])

        if not cart_items:
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(float(item["price"]) * int(item["quantity"]) for item in cart_items)
        order_data = {
            "user": user,
            "total_price": total_price,
            "status": "pendiente",
            "items": [
                {
                    "product": item["id"],
                    "quantity": item["quantity"],
                    "delivery_time": "Entrega inmediata" if item["availability"] == "available" else "Entrega en 5-7 días"
                } for item in cart_items
            ]
        }

        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        stock_movements = []
        updated_stocks = []

        for item in order.items.all():
            stock = Stock.objects.filter(product=item.product).first()
            if item.delivery_time == "Entrega inmediata":
                if not stock or stock.quantity < item.quantity:
                    order.delete()
                    return Response({"error": f"Stock insuficiente para {item.product.name}."},
                                    status=status.HTTP_400_BAD_REQUEST)
                stock.quantity -= item.quantity
                stock.reserved_quantity += item.quantity
                updated_stocks.append(stock)
                stock_movements.append(StockMovement(
                    product=item.product,
                    sales_point=stock.sales_point,
                    change=-item.quantity,
                    reason=f"Reserva para pedido {order.id}"
                ))

        if updated_stocks:
            Stock.objects.bulk_update(updated_stocks, ['quantity', 'reserved_quantity'])
            StockMovement.objects.bulk_create(stock_movements)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class CancelOrderView(APIView):
    """API to cancel an order and release stock"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        if order.status == "enviado":
            return Response({"error": "No se puede cancelar un pedido enviado."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff and order.user != request.user:
            return Response({"error": "No tienes permiso para cancelar este pedido."}, status=status.HTTP_403_FORBIDDEN)

        stock_movements = []
        updated_stocks = []

        for item in order.items.all():
            stock = Stock.objects.filter(product=item.product).first()
            if stock and item.delivery_time == "Entrega inmediata":
                stock.quantity += item.quantity
                stock.reserved_quantity -= item.quantity
                updated_stocks.append(stock)
                stock_movements.append(StockMovement(
                    product=item.product,
                    sales_point=stock.sales_point,
                    change=item.quantity,
                    reason=f"Cancelación de pedido {order.id}"
                ))

        if updated_stocks:
            Stock.objects.bulk_update(updated_stocks, ['quantity', 'reserved_quantity'])
            StockMovement.objects.bulk_create(stock_movements)

        order.status = "cancelado"
        order.save()

        return Response({"message": "Pedido cancelado con éxito."}, status=status.HTTP_200_OK)