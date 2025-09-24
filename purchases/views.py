from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from store.models import Product
from inventory.models import SalesPoint, Stock, StockMovement
from .models import Invoice, InvoiceItem, InvoiceReturn
from .serializers import InvoiceSerializer, InvoiceReturnSerializer
from decimal import Decimal

class InvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        """ This is the definitive fix. It passes the logged-in user to the serializer.
        This ensures that every new invoice has an author. """
        serializer.save(user=self.request.user)

class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Invoice.objects.select_related('user', 'sales_point').prefetch_related("items__product")
        if user.is_staff:
            return base_queryset
        return base_queryset.filter(sales_point__sellers=user)

class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Invoice.objects.select_related('user', 'sales_point').prefetch_related("items__product")
        if user.is_staff:
            return base_queryset
        return base_queryset.filter(sales_point__sellers=user)

class InvoiceUpdateStatusView(generics.UpdateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.all() if user.is_staff else Invoice.objects.filter(sales_point__sellers=user)

    def update(self, request, *args, **kwargs):
        invoice = self.get_object()
        new_status = request.data.get("status")

        if new_status not in ["procesada", "anulada"]:
            return Response({"error": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if invoice.status == "procesada" and new_status == "anulada":
                invoice.revert_stock()
            elif invoice.status == "pendiente" and new_status == "procesada" and invoice.items.exists():
                invoice.update_stock()
            invoice.status = new_status
            invoice.save()

        return Response(InvoiceSerializer(invoice).data)

class InvoiceReturnCreateView(generics.CreateAPIView):
    serializer_class = InvoiceReturnSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        serializer.save()

class InvoiceReturnListView(generics.ListAPIView):
    serializer_class = InvoiceReturnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return InvoiceReturn.objects.prefetch_related("product") if user.is_staff else InvoiceReturn.objects.filter(invoice__sales_point__sellers=user)

class InvoiceReturnDetailView(generics.RetrieveAPIView):
    serializer_class = InvoiceReturnSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return InvoiceReturn.objects.prefetch_related("product") if user.is_staff else InvoiceReturn.objects.filter(invoice__sales_point__sellers=user)
