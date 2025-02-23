from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import F, Q
from store.models import Product, Category
from store.serializers import ProductSerializer, CategorySerializer
from inventory.models import Stock, StockMovement
from inventory.serializers import StockMovementSerializer


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        ✅ Продавцы видят только товары своих точек продаж.
        ✅ Админы видят все товары.
        """
        user = self.request.user
        if user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(stock_info__sales_point__in=user.sales_points.all()).distinct()

    def perform_create(self, serializer):
        """
        ✅ Продавец может добавлять только товары в свои точки продаж.
        """
        user = self.request.user
        product = serializer.save()

        # Автоматически создаём `Stock` для всех точек продаж продавца
        for sales_point in user.sales_points.all():
            Stock.objects.create(product=product, sales_point=sales_point, quantity=0)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        ✅ Продавцы могут редактировать только товары своих точек продаж.
        ✅ Администраторы могут редактировать все товары.
        """
        user = self.request.user
        if user.is_staff:
            return Product.objects.all()
        return Product.objects.filter(stock_info__sales_point__in=user.sales_points.all()).distinct()


class LowStockProductsView(generics.ListAPIView):
    """
    ✅ Показывает товары с низким запасом.
    - Если товаров мало → предупреждение.
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_staff:
            raise PermissionDenied("No tienes permisos para ver el stock bajo.")

        category_id = self.request.query_params.get("category_id")

        # Используем Stock для поиска товаров с низким запасом
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
    ✅ API для просмотра истории складских движений.
    - Фильтры: `product_id`, `date_from`, `date_to`.
    - Доступ только у администраторов.
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
