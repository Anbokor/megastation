from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer
from store.models import Product, StockMovement
from users.permissions import CanAdvanceOrderStatus
from django.shortcuts import get_object_or_404
from .utils import send_order_status_email

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

        total_price = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(user=user, total_price=total_price, status="pendiente")

        order_items = []
        stock_movements = []  # ✅ Логируем изменения склада

        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response({"error": f"Stock insuficiente para {item.product.name}."},
                                status=status.HTTP_400_BAD_REQUEST)

            # 🔥 Списываем товар со склада
            item.product.stock -= item.quantity

            # 🔥 Логируем изменение склада
            stock_movements.append(StockMovement(
                product=item.product,
                change=-item.quantity,
                reason=f"Venta en pedido {order.id}"
            ))

            order_items.append(OrderItem(order=order, product=item.product, quantity=item.quantity))

        # ✅ Массовая вставка в БД
        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update([item.product for item in cart_items], ['stock'])
        StockMovement.objects.bulk_create(stock_movements)  # ✅ Записываем в лог склада

        cart_items.delete()  # 🔥 Очищаем корзину после оформления заказа

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class CancelOrderView(APIView):
    """
    API para cancelar un pedido.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.prefetch_related('items').get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": "El pedido no existe."}, status=status.HTTP_404_NOT_FOUND)

        # 🔥 Проверяем, можно ли отменить заказ
        if order.status == "enviado":
            return Response({"error": "No se puede cancelar un pedido enviado."}, status=status.HTTP_400_BAD_REQUEST)

        # 🔥 Проверяем права доступа
        if not request.user.is_staff and order.user != request.user:
            return Response({"error": "No tienes permiso para cancelar este pedido."}, status=status.HTTP_403_FORBIDDEN)

        # ✅ 1. Дебаг: Выводим список товаров в заказе (убедимся, что список не пуст)
        print(f"Cancelando pedido {order.id}, productos: {[item.product.name for item in order.items.all()]}")

        # 🔥 2. Возвращаем товары на склад
        stock_movements = []
        updated_products = []

        for item in order.items.all():
            item.product.stock += item.quantity  # ✅ Возвращаем товар в stock
            updated_products.append(item.product)  # ✅ Добавляем в список обновлений

            stock_movements.append(StockMovement(
                product=item.product,
                change=item.quantity,
                reason=f"Cancelación de pedido {order.id}"
            ))

        # 🔥 3. Применяем обновления в базе (гарантированно работает)
        if updated_products:
            Product.objects.bulk_update(updated_products, ['stock'])  # ✅ Массово обновляем stock
            StockMovement.objects.bulk_create(stock_movements)  # ✅ Логируем в склад

        # 🔥 4. Меняем статус заказа
        order.status = "cancelado"
        order.save()

        print(f"Pedido {order.id} cancelado. Stock actualizado.")  # ✅ Дебаг

        return Response({"message": "Pedido cancelado con éxito."}, status=status.HTTP_200_OK)

class OrderUpdateView(generics.UpdateAPIView):
    """
    Allows sellers to update order status forward and sends email notifications.
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

        # Отправляем email-уведомление
        send_order_status_email(order.user.email, order.id, new_status)

        return response