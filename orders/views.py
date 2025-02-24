from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from cart.models import CartItem
from store.models import Product
from users.permissions import CanAdvanceOrderStatus
from inventory.models import Stock, StockMovement
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .utils import send_order_status_email
from rest_framework.request import Request
from django.db import transaction

class OrderListView(generics.ListCreateAPIView):
    """✅ API для просмотра списка заказов и создания нового заказа."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """✅ Заказы создаются без резервирования, оно произойдет при оплате."""
        serializer.save(user=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """✅ API для просмотра, обновления и удаления заказа."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        """✅ Обновление заказа с учетом логики резервирования при оплате."""
        instance = serializer.instance
        old_status = instance.status
        new_status = self.request.data.get("status", old_status)

        if old_status != new_status:
            instance.update_status(new_status)

        serializer.save()

class OrderCreateView(generics.CreateAPIView):
    """✅ Создание заказа из корзины с резервированием товара при оплате."""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.price * item.quantity for item in cart_items)
        order = Order.objects.create(user=user, total_price=total_price, status="pendiente")

        order_items = []
        stock_movements = []
        updated_stocks = []

        for item in cart_items:
            stock = Stock.objects.filter(product=item.product).first()
            if not stock or stock.quantity < item.quantity:
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

            order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity))

        OrderItem.objects.bulk_create(order_items)
        Stock.objects.bulk_update(updated_stocks, ['quantity', 'reserved_quantity'])
        StockMovement.objects.bulk_create(stock_movements)

        cart_items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class CancelOrderView(APIView):
    """✅ API для отмены заказа и возврата товаров на склад."""
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
            if stock:
                stock.quantity += item.quantity
                if order.status == "pendiente":
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

class OrderUpdateView(generics.UpdateAPIView):
    """✅ API для обновления заказа (администратор может продвигать статус)."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, CanAdvanceOrderStatus]

    def update(self, request, *args, **kwargs):
        order = get_object_or_404(Order, pk=kwargs["pk"])
        old_status = order.status
        new_status = request.data.get("status")

        if old_status == new_status:
            return Response({"detail": "El estado ya está actualizado."}, status=status.HTTP_400_BAD_REQUEST)

        response = super().update(request, *args, **kwargs)

        send_order_status_email(order.user.email, order.id, new_status)

        return response

class OrderUpdateStatusView(generics.UpdateAPIView):
    """✅ API для обновления статуса заказа с резервированием товара при оплате."""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")

        if not new_status:
            return Response({"error": "Estado requerido."}, status=status.HTTP_400_BAD_REQUEST)

        order.update_status(new_status)
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
