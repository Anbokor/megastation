from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer



class OrderListView(generics.ListAPIView):
    """
    API para listar los pedidos del usuario actual.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()  # 🔥 Admin puede ver todos los pedidos
        return Order.objects.filter(user=user)  # 🔥 Usuario solo ve sus pedidos


class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    API for viewing an order and updating its status (only for admin).
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()  # 🔥 Admin can view and update any order
        return Order.objects.filter(user=user)  # 🔥 Users can only see their own orders

    def perform_update(self, serializer):
        """
        Allows updating only the order status (only for admin).
        """
        request = self.request
        if "status" in request.data:
            if not request.user.is_staff:
                raise ValidationError({"status": "No tienes permiso para cambiar el estado del pedido."})
            serializer.save(status=request.data["status"])  # 🔥 Теперь статус обновляется правильно
        else:
            serializer.save()



class OrderCreateView(generics.CreateAPIView):
    """
    API para crear un pedido a partir del carrito.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        if not cart_items.exists():
            return Response({"error": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        # 🔥 Оптимизируем подсчёт суммы
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # 🔥 Создаём заказ сразу со всеми позициями
        order = Order.objects.create(user=user, total_price=total_price, status="pendiente")

        # 🔥 Используем bulk_create для лучшей производительности
        order_items = [OrderItem(order=order, product=item.product, quantity=item.quantity) for item in cart_items]
        OrderItem.objects.bulk_create(order_items)

        cart_items.delete()  # 🔥 Очищаем корзину после создания заказа

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class CancelOrderView(APIView):
    """
    API for canceling an order.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = Order.objects.filter(pk=pk).first()  # 🔥 Используем `.filter().first()`, чтобы не обрабатывать `DoesNotExist`
        if not order:
            return Response({"error": "El pedido no existe."}, status=status.HTTP_404_NOT_FOUND)

        if order.status == "enviado":
            return Response({"error": "No se puede cancelar un pedido enviado."}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_staff and order.user != request.user:
            return Response({"error": "No tienes permiso para cancelar este pedido."}, status=status.HTTP_403_FORBIDDEN)

        order.status = "cancelado"
        order.save(update_fields=["status"])  # 🔥 Обновляем только одно поле, а не весь объект

        return Response({"message": "Pedido cancelado con éxito."}, status=status.HTTP_200_OK)
