from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import F, Q
from store.models import Product, Category
from store.serializers import ProductSerializer, CategorySerializer
from inventory.models import Stock, StockMovement
from inventory.serializers import StockMovementSerializer
from rest_framework.throttling import ScopedRateThrottle

class CategoryListView(generics.ListCreateAPIView):
    """
    Any user can view categories.
    Only admins can create categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "category_list"

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Any user can view categories.
    Only admins can edit categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "category_list"

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

class ProductListView(generics.ListCreateAPIView):
    """
    Any user can view products.
    Only authenticated sellers or admins can add products.
    """
    serializer_class = ProductSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "product_list"

    def get_queryset(self):
        return Product.objects.all()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Any user can view a product.
    Only sellers or admins can edit/delete.
    """
    serializer_class = ProductSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "product_list"

    def get_queryset(self):
        return Product.objects.all()

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class LowStockProductsView(generics.ListAPIView):
    """
    Shows products with low stock (admin only).
    """
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
    """
    Admins can view stock movement history.
    """
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