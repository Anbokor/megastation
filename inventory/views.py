from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q
from .models import Stock, StockMovement, SalesPoint
from .serializers import StockSerializer, StockMovementSerializer, SalesPointSerializer
from users.models import CustomUser

class StockListView(generics.ListAPIView):
    """
    Allows sellers to view stock levels.
    """
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]

class SalesPointListView(generics.ListAPIView):
    """
    API to list SalesPoints for analytics filtering.
    Accessible to superuser, admin, and store_admin.
    """
    serializer_class = SalesPointSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return SalesPoints based on user role:
        - superuser and admin see all SalesPoints.
        - store_admin sees only their assigned SalesPoint.
        """
        user = self.request.user
        if user.role in [CustomUser.Role.SUPERUSER, CustomUser.Role.ADMIN]:
            return SalesPoint.objects.all()
        elif user.role == CustomUser.Role.STORE_ADMIN and user.sales_point:
            return SalesPoint.objects.filter(id=user.sales_point.id)
        return SalesPoint.objects.none()

class StockMovementListCreateView(generics.ListCreateAPIView):
    """
    API for listing and creating stock movements.
    """
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]