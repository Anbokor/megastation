from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import F, Q, Sum
from store.models import Product, Category
from store.serializers import ProductSerializer, CategorySerializer
from inventory.models import Stock, StockMovement
from inventory.serializers import StockMovementSerializer
from rest_framework.throttling import ScopedRateThrottle

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "category_list"

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "category_list"

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "product_list"

    def get_queryset(self):
        return Product.objects.all()

    def get_serializer_context(self):
        """
        This is the final, correct fix. This method ensures that the serializer
        always receives the necessary context, regardless of where it's called from.
        """
        # Start with the default context
        context = super().get_serializer_context()
        
        # Get all product IDs from the queryset that will be listed
        product_ids = self.get_queryset().values_list('id', flat=True)
        
        # Calculate the available stock for all products in a single query.
        stocks = Stock.objects.filter(product_id__in=product_ids)\
            .values('product_id')\
            .annotate(available_stock=Sum(F('quantity') - F('reserved_quantity')))
            
        # Create the stock map
        stock_map = {s['product_id']: s['available_stock'] for s in stocks}
        
        # Add the stock map to the context
        context['product_stock_map'] = stock_map
        
        return context

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "product_list"

    def get_queryset(self):
        return Product.objects.all()
    
    # FIX: Also apply the context fix to the detail view
    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_id = self.kwargs.get('pk') # Get product ID from URL
        if product_id:
            stocks = Stock.objects.filter(product_id=product_id)\
                .values('product_id')\
                .annotate(available_stock=Sum(F('quantity') - F('reserved_quantity')))
            stock_map = {s['product_id']: s['available_stock'] for s in stocks}
            context['product_stock_map'] = stock_map
        return context

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class LowStockProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        category_id = self.request.query_params.get("category_id")
        low_stock_products = Stock.objects.filter(
            quantity__lt=F("product__category__min_stock")
        ).select_related("product")
        if category_id:
            low_stock_products = low_stock_products.filter(product__category_id=category_id)
        return [stock.product for stock in low_stock_products]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:
            return Response({"message": "No hay productos con stock bajo."})
        return super().list(request, *args, **kwargs)

class StockMovementListView(generics.ListAPIView):
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        queryset = StockMovement.objects.all().order_by("-created_at")
        product_id = self.request.query_params.get("product_id")
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        filters = Q()
        if product_id:
            filters &= Q(product_id=product_id)
        if date_from:
            filters &= Q(created_at__gte=date_from)
        if date_to:
            filters &= Q(created_at__lte=date_to)
        return queryset.filter(filters)
