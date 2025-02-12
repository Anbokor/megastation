from .models import Category, Product, StockMovement
from .serializers import CategorySerializer, ProductSerializer, StockMovementSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import F
from rest_framework.exceptions import PermissionDenied
from users.permissions import IsAdmin, IsStoreAdmin, IsSeller, IsCustomer  # ✅ Подключаем кастомные права доступа
from rest_framework.request import Request

### ✅ Категории товаров (только администраторы)
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]  # ✅ Только админы

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]  # ✅ Только админы

### ✅ Товары
class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """
        ✅ Все могут просматривать товары.
        ✅ Только администраторы и продавцы могут добавлять новые товары.
        """
        if self.request.method == 'POST':
            return [IsAdmin | IsStoreAdmin | IsSeller()]  # 🔥 Продавцы могут создавать товары
        return [permissions.AllowAny()]

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        """
        ✅ Все могут просматривать товары.
        ✅ Только администраторы и продавцы могут редактировать и удалять.
        """
        if self.request.method in ['PUT', 'DELETE']:
            return [IsAdmin | IsStoreAdmin | IsSeller()]
        return [permissions.AllowAny()]

### ✅ Товары с низким остатком (только администраторы и продавцы)
class LowStockProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAdmin | IsStoreAdmin]  # ✅ Только админы и админы магазинов

    def get_queryset(self):
        """
        ✅ Возвращает товары, у которых остаток ниже минимального уровня.
        """
        return Product.objects.filter(stock__lt=F('category__min_stock'))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No hay productos con stock bajo."})
        return super().list(request, *args, **kwargs)

### ✅ История движения товара (только администраторы и админы магазинов)
class StockMovementListView(generics.ListAPIView):
    """
    API para obtener el historial de movimientos de stock.
    """
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAdminUser]  # ✅ Доступ только для админов

    def get_queryset(self):
        """
        ✅ Фильтрация по product_id, если передан параметр.
        """
        request = self.request  # 🔥 Теперь `request` будет объектом `Request`, а не `HttpRequest`

        if isinstance(request, Request):  # ✅ Проверяем, что это `Request`
            product_id = request.query_params.get("product_id")
        else:
            product_id = None  # 🔥 На случай, если что-то пошло не так

        queryset = StockMovement.objects.all().order_by("-created_at")

        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset