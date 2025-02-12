from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from store.serializers import ProductSerializer
from django.db.models import F  # 🔥 Импортируем F для работы с полями моделей
from rest_framework.exceptions import PermissionDenied
class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method == 'POST':  # Только продавцы и админы могут добавлять товары
            return [permissions.IsAdminUser()]
        return []

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:  # Только админы и продавцы могут редактировать товары
            return [permissions.IsAdminUser()]
        return []

class LowStockProductsView(generics.ListAPIView):
    """
    API para obtener productos con stock bajo (solo administradores).
    """
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:  # 🔥 Проверяем, что это админ
            raise PermissionDenied("No tienes permisos para ver el stock bajo.")

        return Product.objects.filter(stock__lt=F('category__min_stock'))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response({"message": "No hay productos con stock bajo."})
        return super().list(request, *args, **kwargs)