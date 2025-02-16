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


class OrderListView(generics.ListAPIView):
    """
    ✅ API para listar los pedidos del usuario actual.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.all() if user.is_staff else Order.objects.filter(user=user)


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    ✅ API para ver y actualizar un pedido (solo admin puede actualizar).
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.all() if user.is_staff else Order.objects.filter(user=user)

    def perform_update(self, serializer):
        request = self.request
        if isinstance(request, Request):
            if "status" in request.data:
                if not request.user.is_staff:
                    raise ValidationError({"status": "No tienes permiso para cambiar el estado del pedido."})

                order = self.get_object()
                old_status = order.status
                new_status = request.data["status"]

                if old_status in ["pendiente", "en_proceso"] and new_status == "enviado":
                    self.finalize_stock(order)

                serializer.save(status=new_status)
            else:
                serializer.save()
        else:
            raise ValidationError("Error interno: request no es un objeto válido de DRF.")

    def finalize_stock(self, order):
        """
        ✅ Окончательно списывает товар при отправке заказа.
        """
        stock_movements = []
        for item in order.items.all():
            stock = Stock.objects.filter(product=item.product).first()
            if stock:
                stock.quantity -= item.quantity
                stock.save()

                stock_movements.append(StockMovement(
                    product=item.product,
                    change=-item.quantity,
                    reason=f"Pedido enviado {order.id}"
                ))

        if stock_movements:
            StockMovement.objects.bulk_create(stock_movements)


class OrderCreateView(generics.CreateAPIView):
    """
    ✅ API para crear un pedido a partir del carrito.
    """
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
            updated_stocks.append(stock)

            stock_movements.append(StockMovement(
                product=item.product,
                change=-item.quantity,
                reason=f"Reserva para pedido {order.id}"
            ))

            order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity))

        OrderItem.objects.bulk_create(order_items)
        Stock.objects.bulk_update(updated_stocks, ['quantity'])
        StockMovement.objects.bulk_create(stock_movements)

        cart_items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    """
    ✅ API para cancelar un pedido y devolver stock.
    """
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
                updated_stocks.append(stock)

                stock_movements.append(StockMovement(
                    product=item.product,
                    change=item.quantity,
                    reason=f"Cancelación de pedido {order.id}"
                ))

        if updated_stocks:
            Stock.objects.bulk_update(updated_stocks, ['quantity'])
            StockMovement.objects.bulk_create(stock_movements)

        order.status = "cancelado"
        order.save()

        return Response({"message": "Pedido cancelado con éxito."}, status=status.HTTP_200_OK)


class OrderUpdateView(generics.UpdateAPIView):
    """
    ✅ Allows sellers to update order status forward and sends email notifications.
    """
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
