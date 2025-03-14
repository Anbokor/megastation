from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F, Q, Avg
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
import logging
from users.permissions import IsSuperuser, IsAdmin, IsStoreAdmin
from orders.models import Order, OrderItem
from store.models import Product
from inventory.models import Stock, StockMovement
from purchases.models import Invoice

logger = logging.getLogger(__name__)

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, (IsSuperuser | IsAdmin | IsStoreAdmin)]

    def get(self, request):
        try:
            user = request.user
            time_filter = request.query_params.get('time_filter', 'month')
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')

            # Define time range
            now = timezone.now()
            if start_date_str and end_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            else:
                if time_filter == 'day':
                    start_date = now - timedelta(days=1)
                elif time_filter == 'week':
                    start_date = now - timedelta(weeks=1)
                else:  # month
                    start_date = now - timedelta(days=30)
                end_date = now

            # Base time filters
            order_filter = Q(created_at__gte=start_date, created_at__lte=end_date)
            invoice_filter = Q(created_at__gte=start_date, created_at__lte=end_date) & Q(status='procesada')
            stock_movement_filter = Q(created_at__gte=start_date, created_at__lte=end_date)

            if user.role in ['superuser', 'admin']:
                # Full statistics for superuser and admin
                product_stats = Stock.objects.aggregate(
                    total_products=Count('id'),
                    low_stock_count=Count('id', filter=Q(quantity__lte=F('low_stock_threshold'))),
                    avg_stock_level=Avg('quantity')
                )
                order_stats = Order.objects.filter(order_filter).aggregate(
                    total_orders=Count('id'),
                    total_revenue=Sum('total_price')
                )
                purchase_stats = Invoice.objects.filter(invoice_filter).aggregate(
                    total_purchases=Count('id'),
                    total_purchase_cost=Sum(F('items__quantity') * F('items__cost_per_item'), filter=Q(items__quantity__gt=0))
                )
                daily_sales = Order.objects.filter(order_filter).annotate(
                    day=TruncDay('created_at')
                ).values('day').annotate(
                    revenue=Sum('total_price'),
                    orders=Count('id')
                ).order_by('day')
                daily_purchases = Invoice.objects.filter(invoice_filter).annotate(
                    day=TruncDay('created_at')
                ).values('day').annotate(
                    cost=Sum(F('items__quantity') * F('items__cost_per_item')),
                    purchases=Count('id')
                ).order_by('day')
                daily_stock = StockMovement.objects.filter(stock_movement_filter).annotate(
                    day=TruncDay('created_at')
                ).values('day').annotate(
                    change=Sum('change')
                ).order_by('day')
                top_sold_products = OrderItem.objects.filter(order__created_at__gte=start_date, order__created_at__lte=end_date).values(
                    'product__name'
                ).annotate(
                    total_sold=Sum('quantity')
                ).order_by('-total_sold')[:5]
                top_purchased_products = Invoice.objects.filter(invoice_filter).values(
                    'items__product__name'
                ).annotate(
                    total_purchased=Sum('items__quantity')
                ).order_by('-total_purchased')[:5]
            elif user.role == 'store_admin' and user.sales_point:
                # Statistics for store_admin limited to their sales point
                product_stats = Stock.objects.filter(sales_point=user.sales_point).aggregate(
                    total_products=Count('id'),
                    low_stock_count=Count('id', filter=Q(quantity__lte=F('low_stock_threshold'))),
                    avg_stock_level=Avg('quantity')
                )
                order_stats = Order.objects.filter(order_filter, items__product__stock_info__sales_point=user.sales_point).aggregate(
                    total_orders=Count('id', distinct=True),
                    total_revenue=Sum('total_price')
                )
                purchase_stats = Invoice.objects.filter(invoice_filter, sales_point=user.sales_point).aggregate(
                    total_purchases=Count('id'),
                    total_purchase_cost=Sum(F('items__quantity') * F('items__cost_per_item'), filter=Q(items__quantity__gt=0))
                )
                daily_sales = Order.objects.filter(order_filter, items__product__stock_info__sales_point=user.sales_point).annotate(
                    day=TruncDay('created_at')
                ).values('day').annotate(
                    revenue=Sum('total_price'),
                    orders=Count('id', distinct=True)
                ).order_by('day')
                daily_purchases = Invoice.objects.filter(invoice_filter, sales_point=user.sales_point).annotate(
                    day=TruncDay('created_at')
                ).values('day').annotate(
                    cost=Sum(F('items__quantity') * F('items__cost_per_item')),
                    purchases=Count('id')
                ).order_by('day')
                daily_stock = StockMovement.objects.filter(stock_movement_filter, sales_point=user.sales_point).annotate(
                    day=TruncDay('created_at')
                ).values('day').annotate(
                    change=Sum('change')
                ).order_by('day')
                top_sold_products = OrderItem.objects.filter(
                    order__created_at__gte=start_date,
                    order__created_at__lte=end_date,
                    product__stock_info__sales_point=user.sales_point
                ).values('product__name').annotate(
                    total_sold=Sum('quantity')
                ).order_by('-total_sold')[:5]
                top_purchased_products = Invoice.objects.filter(
                    invoice_filter,
                    sales_point=user.sales_point
                ).values('items__product__name').annotate(
                    total_purchased=Sum('items__quantity')
                ).order_by('-total_purchased')[:5]
            else:
                return Response({'error': 'Permiso denegado'}, status=403)

            return Response({
                'product_statistics': {
                    'total_products': product_stats['total_products'] or 0,
                    'low_stock_count': product_stats['low_stock_count'] or 0,
                    'avg_stock_level': float(product_stats['avg_stock_level'] or 0),
                    'daily_stock': list(daily_stock)
                },
                'order_statistics': {
                    'total_orders': order_stats['total_orders'] or 0,
                    'total_revenue': float(order_stats['total_revenue'] or 0),
                    'daily_sales': list(daily_sales),
                    'top_sold_products': list(top_sold_products)
                },
                'purchase_statistics': {
                    'total_purchases': purchase_stats['total_purchases'] or 0,
                    'total_purchase_cost': float(purchase_stats['total_purchase_cost'] or 0) if purchase_stats['total_purchase_cost'] else 0,
                    'daily_purchases': list(daily_purchases),
                    'top_purchased_products': list(top_purchased_products)
                }
            })
        except Exception as e:
            logger.error(f"Error in analytics view: {str(e)}", exc_info=True)
            return Response({'error': 'Error interno del servidor'}, status=500)