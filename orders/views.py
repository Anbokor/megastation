from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, F, Sum
from store.models import Product
from users.models import CustomUser
from users.permissions import IsSuperuser, IsAdmin, IsStoreAdmin
from inventory.models import Stock, SalesPoint
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .tasks import send_order_notification_emails
from django.db import transaction
import mercadopago
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'items__product').order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items', 'items__product')

class OrderCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = request.data.get("items", [])
        payment_method = request.data.get("payment_method", "cash")

        if not cart_items:
            return Response({"detail": "El carrito está vacío."}, status=status.HTTP_400_BAD_REQUEST)

        aggregated_items = defaultdict(int)
        for item in cart_items:
            try:
                product_id = int(item['id'])
                quantity = int(item['quantity'])
                if quantity <= 0:
                    return Response({"detail": f"La cantidad para el producto ID {product_id} debe ser positiva."},
                                    status=status.HTTP_400_BAD_REQUEST)
                aggregated_items[product_id] += quantity
            except (ValueError, TypeError, KeyError):
                return Response({"detail": "Datos de carrito inválidos: ID y cantidad deben ser números."},
                                status=status.HTTP_400_BAD_REQUEST)

        total_price = Decimal('0.0')
        total_cost_price = Decimal('0.0')
        order_items_to_create = []
        stocks_to_update = []

        product_ids = list(aggregated_items.keys())
        products = Product.objects.filter(id__in=product_ids).in_bulk()

        for product_id, quantity in aggregated_items.items():
            product = products.get(product_id)
            if not product:
                return Response({"detail": f"Producto con ID {product_id} no encontrado."},
                                status=status.HTTP_400_BAD_REQUEST)

            stock_info = Stock.objects.filter(product_id=product_id).aggregate(
                total_available=Sum(F('quantity') - F('reserved_quantity'))
            )
            total_available = stock_info.get('total_available') or 0

            if total_available < quantity:
                return Response({"detail": f"Stock insuficiente para '{product.name}'. Hay {total_available} disponibles en total."},
                                status=status.HTTP_400_BAD_REQUEST)

            quantity_to_reserve = quantity
            product_stocks = Stock.objects.select_for_update().filter(product_id=product_id)
            
            for stock in product_stocks:
                if quantity_to_reserve <= 0:
                    break
                
                available_in_this_stock = stock.quantity - stock.reserved_quantity
                reserve_from_this = min(quantity_to_reserve, available_in_this_stock)

                if reserve_from_this > 0:
                    stock.reserved_quantity += reserve_from_this
                    stocks_to_update.append(stock)
                    quantity_to_reserve -= reserve_from_this

            item_price = product.price
            # FIX: Safely get cost_price, defaulting to 0 if not present.
            item_cost_price = getattr(product, 'cost_price', 0)

            total_price += item_price * quantity
            total_cost_price += item_cost_price * quantity

            order_items_to_create.append(
                OrderItem(
                    product=product,
                    quantity=quantity,
                    price=item_price,  # Use the correct price at the time of order
                    cost_price=item_cost_price # Use the safely obtained cost price
                )
            )

        order_status = 'en_proceso' if payment_method == 'card' else 'pendiente'
        order = Order.objects.create(
            user=user,
            total_price=total_price,
            total_cost_price=total_cost_price,
            status=order_status,
            payment_method=payment_method
        )

        for item in order_items_to_create:
            item.order = order
        
        OrderItem.objects.bulk_create(order_items_to_create)
        Stock.objects.bulk_update(list(set(stocks_to_update)), ['reserved_quantity'])

        try:
            product_ids_in_order = [item.product.id for item in order_items_to_create]
            sales_points = SalesPoint.objects.filter(
                stock__product_id__in=product_ids_in_order
            ).distinct()
            for sales_point in sales_points:
                staff_emails = list(sales_point.administrators.values_list('email', flat=True)) + \
                               list(sales_point.sellers.values_list('email', flat=True))
                if staff_emails:
                    send_order_notification_emails(
                        order_id=order.id,
                        sales_point_id=sales_point.id,
                        staff_emails=staff_emails,
                    )
        except Exception as e:
            logger.error(f"Failed to send order notification email for order {order.id}: {e}")

        return Response({'id': order.id}, status=status.HTTP_201_CREATED)

class CreatePaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        order = get_object_or_404(Order, id=order_id, user=request.user)

        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        items = [{
            "title": item.product.name,
            "quantity": item.quantity,
            "unit_price": float(item.product.price),
        } for item in order.items.all()]

        preference_data = {
            "items": items,
            "back_urls": {
                "success": "http://localhost:5173/checkout/success",
                "failure": "http://localhost:5173/checkout/failure",
            },
            "auto_return": "approved",
            "notification_url": request.build_absolute_uri(f'/api/orders/webhook/'),
            "external_reference": order.id,
        }

        try:
            preference_response = sdk.preference().create(preference_data)
            return Response({'init_point': preference_response["response"]['init_point']})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(csrf_exempt, name='dispatch')
class MercadoPagoWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        notification = request.data
        if notification.get('type') == 'payment':
            payment_id = notification.get('data', {}).get('id')
            if not payment_id:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            try:
                sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
                payment_info = sdk.payment().get(payment_id)
                payment = payment_info['response']
                order_id = payment.get('external_reference')
                order = get_object_or_404(Order, id=order_id)

                if payment['status'] == 'approved':
                    order.status = 'en_proceso'
                    order.save()
                elif payment['status'] in ['rejected', 'cancelled']:
                    order.status = 'fallido'
                    order.save()

            except Exception as e:
                logger.error(f"Error processing MercadoPago webhook: {e}", exc_info=True)
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)

class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)

        if order.status not in ['pendiente', 'en_proceso']:
            return Response({"error": f"No se puede cancelar un pedido en estado '{order.status}'."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            self._release_stock_for_order(order)
            order.status = "cancelado"
            order.save()

        return Response({"message": "Pedido cancelado con éxito."})
    
    def _release_stock_for_order(self, order):
        stocks_to_update = []
        for item in order.items.all():
            quantity_to_return = item.quantity
            product_stocks = Stock.objects.select_for_update().filter(product=item.product)
            
            for stock in product_stocks:
                if quantity_to_return <= 0:
                    break
                
                can_return = min(quantity_to_return, stock.reserved_quantity)
                if can_return > 0:
                    stock.reserved_quantity -= can_return
                    stocks_to_update.append(stock)
                    quantity_to_return -= can_return

        if stocks_to_update:
            Stock.objects.bulk_update(list(set(stocks_to_update)), ['reserved_quantity'])


class StaffOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, (IsSuperuser | IsAdmin | IsStoreAdmin)]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Order.objects.select_related('user').prefetch_related('items', 'items__product')

        if user.role in ['superuser', 'admin']:
            return base_queryset.order_by('-created_at')
        
        if user.role == 'store_admin' and hasattr(user, 'sales_point') and user.sales_point:
            return base_queryset.filter(
                items__product__stock_info__sales_point=user.sales_point
            ).distinct().order_by('-created_at')

        return Order.objects.none()

class StaffOrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, (IsSuperuser | IsAdmin | IsStoreAdmin)]
    queryset = Order.objects.all().prefetch_related('items', 'items__product', 'user')

    def update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get('status')
        original_status = order.status

        if not new_status:
            return Response({"error": "El campo 'status' es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status == original_status:
            return Response(self.get_serializer(order).data)

        allowed_transitions = {
            'pendiente': ['en_proceso', 'cancelado'],
            'en_proceso': ['enviado', 'completado', 'cancelado'],
            'enviado': ['completado'],
            'completado': [],
            'cancelado': [],
            'fallido': ['pendiente']
        }

        if new_status not in allowed_transitions.get(original_status, []):
            return Response({
                "error": f"No se puede cambiar el estado de '{original_status}' a '{new_status}'."
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                if new_status in ['enviado', 'completado'] and original_status not in ['enviado', 'completado']:
                    self._fulfill_stock_for_order(order)
                
                elif new_status == 'cancelado':
                    self._release_stock_for_order(order)

                order.status = new_status
                order.save()

        except Exception as e:
            logger.error(f"Error updating order {order.id} status: {e}", exc_info=True)
            return Response({"error": "Ocurrió un error interno al actualizar el pedido."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(self.get_serializer(order).data)

    def _release_stock_for_order(self, order):
        cancel_view = CancelOrderView()
        cancel_view._release_stock_for_order(order)

    def _fulfill_stock_for_order(self, order):
        stocks_to_update = []
        for item in order.items.all():
            quantity_to_fulfill = item.quantity
            product_stocks = Stock.objects.select_for_update().filter(product=item.product)

            for stock in product_stocks:
                if quantity_to_fulfill <= 0: break
                
                fulfill_from_this = min(quantity_to_fulfill, stock.reserved_quantity)
                if fulfill_from_this > 0:
                    stock.quantity -= fulfill_from_this
                    stock.reserved_quantity -= fulfill_from_this
                    stocks_to_update.append(stock)
                    quantity_to_fulfill -= fulfill_from_this
            
            if quantity_to_fulfill > 0:
                raise Exception(f"No se pudo cumplir con el stock reservado para el producto {item.product.id}")

        if stocks_to_update:
            Stock.objects.bulk_update(list(set(stocks_to_update)), ['quantity', 'reserved_quantity'])
