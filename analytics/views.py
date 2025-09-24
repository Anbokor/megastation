from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, F, Q, Avg, DecimalField
from django.db.models.functions import Coalesce, TruncDay
from django.utils import timezone
from datetime import timedelta, datetime
import logging
from decimal import Decimal
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from users.permissions import IsSuperuser, IsAdmin, IsStoreAdmin
from orders.models import Order, OrderItem
from inventory.models import Stock
from purchases.models import Invoice, InvoiceItem

logger = logging.getLogger(__name__)

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, (IsSuperuser | IsAdmin | IsStoreAdmin)]

    @method_decorator(cache_page(600)) # Cache this view for 10 minutes
    def get(self, request):
        try:
            # --- 1. Get Filters ---
            start_date, end_date = self._get_date_filters(request)
            sales_point_id = request.query_params.get('sales_point_id')

            # --- 2. Filter QuerySets based on Role and Filters ---
            order_items_qs = self._get_filtered_order_items(request, start_date, end_date)
            invoices_qs = self._get_filtered_invoices(request, start_date, end_date)
            stock_qs = self._get_filtered_stock(request)

            # --- 3. Calculate KPIs ---
            kpis = self._calculate_kpis(order_items_qs, invoices_qs, stock_qs)

            # --- 4. Get Time Series Data ---
            daily_sales = self._get_daily_sales(order_items_qs)
            daily_purchases = self._get_daily_purchases(invoices_qs)
            daily_profit = self._get_daily_profit(order_items_qs)

            # --- 5. Get Top Lists ---
            top_sold_products = self._get_top_sold_products(order_items_qs)
            top_customers = self._get_top_customers(order_items_qs)
            top_profitable_products = self._get_top_profitable_products(order_items_qs)

            # --- 6. Assemble Response ---
            return Response({
                'kpis': kpis,
                'time_series': {
                    'sales': daily_sales,
                    'purchases': daily_purchases,
                    'profit': daily_profit,
                },
                'top_lists': {
                    'sold_products': top_sold_products,
                    'customers': top_customers,
                    'profitable_products': top_profitable_products,
                }
            })

        except Exception as e:
            logger.error(f"Error in AnalyticsView: {str(e)}", exc_info=True)
            return Response({'error': 'An internal server error occurred.'}, status=500)

    def _get_date_filters(self, request):
        time_filter = request.query_params.get('time_filter', 'month')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            end_date = (datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)).replace(tzinfo=timezone.utc)
        else:
            end_date = timezone.now()
            if time_filter == 'day':
                start_date = end_date - timedelta(days=1)
            elif time_filter == 'week':
                start_date = end_date - timedelta(weeks=1)
            else:  # month by default
                start_date = end_date - timedelta(days=30)
        return start_date, end_date

    def _get_base_order_items(self, start_date, end_date):
        # Filter orders that are not cancelled
        return OrderItem.objects.filter(
            order__created_at__range=(start_date, end_date),
            order__status__in=['en_proceso', 'enviado'] # Consider only processed or shipped orders
        )

    def _get_base_invoices(self, start_date, end_date):
        return Invoice.objects.filter(created_at__range=(start_date, end_date), status='procesada')

    def _get_filtered_order_items(self, request, start_date, end_date):
        qs = self._get_base_order_items(start_date, end_date)
        user = request.user
        sales_point_id = request.query_params.get('sales_point_id')
        if user.role == 'store_admin' and user.sales_point:
            return qs.filter(sales_point=user.sales_point)
        if sales_point_id and user.role in ['superuser', 'admin']:
            return qs.filter(sales_point_id=sales_point_id)
        return qs

    def _get_filtered_invoices(self, request, start_date, end_date):
        qs = self._get_base_invoices(start_date, end_date)
        user = request.user
        sales_point_id = request.query_params.get('sales_point_id')
        if user.role == 'store_admin' and user.sales_point:
            return qs.filter(sales_point=user.sales_point)
        if sales_point_id and user.role in ['superuser', 'admin']:
            return qs.filter(sales_point_id=sales_point_id)
        return qs

    def _get_filtered_stock(self, request):
        user = request.user
        sales_point_id = request.query_params.get('sales_point_id')
        qs = Stock.objects.all()
        if user.role == 'store_admin' and user.sales_point:
            return qs.filter(sales_point=user.sales_point)
        if sales_point_id and user.role in ['superuser', 'admin']:
            return qs.filter(sales_point_id=sales_point_id)
        return qs

    def _calculate_kpis(self, order_items_qs, invoices_qs, stock_qs):
        # Correctly calculate revenue and cost of goods sold (COGS) from OrderItems
        sales_stats = order_items_qs.aggregate(
            total_revenue=Coalesce(Sum(F('quantity') * F('price')), Decimal(0), output_field=DecimalField()),
            total_cogs=Coalesce(Sum(F('quantity') * F('cost_price')), Decimal(0), output_field=DecimalField()),
            total_orders=Count('order', distinct=True)
        )
        total_revenue = sales_stats['total_revenue']
        total_cogs = sales_stats['total_cogs']
        total_orders = sales_stats['total_orders']

        # Purchase cost is now a separate metric for tracking expenses
        purchase_stats = InvoiceItem.objects.filter(invoice__in=invoices_qs).aggregate(
            total_purchase_cost=Coalesce(Sum(F('quantity') * F('cost_per_item')), Decimal(0), output_field=DecimalField())
        )
        total_purchase_cost = purchase_stats['total_purchase_cost']

        # Stock KPIs
        low_stock_count = stock_qs.filter(quantity__lte=F('low_stock_threshold')).count()

        # Correctly calculated KPIs
        net_profit = total_revenue - total_cogs
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
        avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0

        return {
            'total_revenue': total_revenue,
            'total_cost_of_goods_sold': total_cogs, # Renamed for clarity
            'net_profit': net_profit,
            'profit_margin': profit_margin,
            'total_orders': total_orders,
            'avg_order_value': avg_order_value,
            'low_stock_count': low_stock_count,
            'total_purchase_cost': total_purchase_cost, # Informational metric
        }

    def _get_daily_sales(self, order_items_qs):
        return list(order_items_qs.annotate(day=TruncDay('order__created_at'))
            .values('day')
            .annotate(revenue=Sum(F('quantity') * F('price'))) # Use stored price
            .order_by('day'))

    def _get_daily_purchases(self, invoices_qs):
        return list(InvoiceItem.objects.filter(invoice__in=invoices_qs)
            .annotate(day=TruncDay('invoice__created_at'))
            .values('day')
            .annotate(cost=Sum(F('quantity') * F('cost_per_item')))
            .order_by('day'))

    def _get_daily_profit(self, order_items_qs):
        return list(order_items_qs.annotate(day=TruncDay('order__created_at'))
            .values('day')
            .annotate(
                daily_revenue=Sum(F('quantity') * F('price')),
                daily_cogs=Sum(F('quantity') * F('cost_price'))
            )
            .annotate(profit=F('daily_revenue') - F('daily_cogs'))
            .values('day', 'profit')
            .order_by('day'))

    def _get_top_sold_products(self, order_items_qs):
        return list(order_items_qs.values('product__name')
            .annotate(total_quantity=Sum('quantity'))
            .order_by('-total_quantity')[:5])

    def _get_top_customers(self, order_items_qs):
        return list(order_items_qs.values('order__user__username')
            .annotate(total_revenue=Sum(F('quantity') * F('price'))) # Use stored price
            .order_by('-total_revenue')[:5])

    def _get_top_profitable_products(self, order_items_qs):
        return list(order_items_qs.values('product__name')
            .annotate(
                total_revenue=Sum(F('quantity') * F('price')),
                total_cogs=Sum(F('quantity') * F('cost_price'))
            )
            .annotate(total_profit=F('total_revenue') - F('total_cogs'))
            .order_by('-total_profit')[:5])
