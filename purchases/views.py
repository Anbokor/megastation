from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Sum
from store.models import Product
from inventory.models import SalesPoint, Stock, StockMovement
from .models import Invoice, InvoiceItem, InvoiceReturn
from .serializers import InvoiceSerializer, InvoiceReturnSerializer

class InvoiceCreateView(generics.CreateAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = request.data
        invoice_number = data.get("invoice_number")
        supplier = data.get("supplier")
        sales_point_id = data.get("sales_point")
        user = request.user
        items_data = data.get("items", [])

        if not all([invoice_number, supplier, sales_point_id, items_data]):
            return Response({"error": "Faltan datos."}, status=status.HTTP_400_BAD_REQUEST)

        if Invoice.objects.filter(invoice_number=invoice_number).exists():
            return Response({"error": "Número de factura ya existe."}, status=status.HTTP_400_BAD_REQUEST)

        sales_point = get_object_or_404(SalesPoint, id=sales_point_id)

        with transaction.atomic():
            invoice = Invoice.objects.create(
                invoice_number=invoice_number, supplier=supplier, user=user, sales_point=sales_point,
                status=data.get("status", "pendiente")
            )

            invoice_items = []
            stock_updates = []
            stock_movements = []

            for item in items_data:
                product = get_object_or_404(Product, id=item.get("product_id"))
                purchase_price = float(item.get("purchase_price"))
                quantity = int(item.get("quantity"))

                if quantity <= 0:
                    return Response({"error": f"La cantidad de {product.name} debe ser mayor que 0."},
                                    status=status.HTTP_400_BAD_REQUEST)

                product.price = purchase_price * 1.2
                product.save()

                stock, created = Stock.objects.get_or_create(
                    product=product, sales_point=sales_point, defaults={"quantity": 0}
                )
                stock.quantity += quantity
                stock_updates.append(stock)

                stock_movements.append(StockMovement(
                    product=product, sales_point=sales_point, change=quantity,
                    reason=f"Recepción de factura {invoice.invoice_number}"
                ))

                invoice_items.append(InvoiceItem(
                    invoice=invoice, product=product, quantity=quantity, cost_per_item=purchase_price
                ))

            InvoiceItem.objects.bulk_create(invoice_items)
            Stock.objects.bulk_update(stock_updates, ["quantity"])
            StockMovement.objects.bulk_create(stock_movements)

            if invoice.status == "procesada":
                invoice.update_stock()

        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)

class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.prefetch_related("items__product") if user.is_staff else Invoice.objects.filter(sales_point__sellers=user)

class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.prefetch_related("items__product") if user.is_staff else Invoice.objects.filter(sales_point__sellers=user)

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

    def create(self, request, *args, **kwargs):
        data = request.data
        invoice = get_object_or_404(Invoice, id=data.get("invoice_id"))
        product = get_object_or_404(Product, id=data.get("product_id"))
        sales_point = get_object_or_404(SalesPoint, id=data.get("sales_point_id"))
        quantity = int(data.get("quantity"))
        reason = data.get("reason")

        if invoice.status in ["anulada", "pendiente"]:
            return Response({"error": f"No se puede devolver productos de una factura {invoice.status}."},
                            status=status.HTTP_400_BAD_REQUEST)

        if quantity <= 0:
            return Response({"error": "La cantidad de devolución debe ser mayor que 0."},
                            status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            return_entry = InvoiceReturn(
                invoice=invoice, product=product, sales_point=sales_point, quantity=quantity, reason=reason
            )
            return_entry.save()  # Логика списания теперь в модели

        return Response(InvoiceReturnSerializer(return_entry).data, status=status.HTTP_201_CREATED)

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