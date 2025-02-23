from rest_framework import generics, permissions
from .models import Stock, SalesPoint, StockMovement
from .serializers import StockSerializer, SalesPointSerializer, StockMovementSerializer
from django.db.models import Q

class StockListView(generics.ListAPIView):
    """
    Позволяет продавцам видеть остатки товаров.
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

class SalesPointListView(generics.ListCreateAPIView):
    """✅ API управления точками продаж"""
    serializer_class = SalesPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return SalesPoint.objects.all()
        return SalesPoint.objects.filter(Q(sellers=user) | Q(administrators=user)).distinct()

    def perform_create(self, serializer):
        """✅ Автоматически добавляем текущего пользователя в администраторы при создании"""
        sales_point = serializer.save()
        sales_point.administrators.add(self.request.user)

class StockMovementListCreateView(generics.ListCreateAPIView):
    """
    ✅ API для списка перемещений товаров.
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]