from rest_framework import generics, permissions, status
from rest_framework.response import Response
from store.models import Product
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer


class InvoiceCreateView(generics.CreateAPIView):
    """
    API para registrar una nueva factura de compra.
    """
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = request.data
        invoice_number = data.get("invoice_number")  # 🔥 Получаем номер накладной
        supplier = data.get("supplier")
        user = request.user
        items_data = data.get("items", [])

        if not invoice_number or not supplier or not items_data:
            return Response({"error": "Faltan datos."}, status=status.HTTP_400_BAD_REQUEST)

        if Invoice.objects.filter(invoice_number=invoice_number).exists():
            return Response({"error": "Número de factura ya existe."}, status=status.HTTP_400_BAD_REQUEST)

        invoice = Invoice.objects.create(invoice_number=invoice_number, supplier=supplier, user=user)

        order_items = []
        for item in items_data:
            product = Product.objects.get(id=item["product_id"])
            purchase_price = item["purchase_price"]
            quantity = item["quantity"]

            product.price = purchase_price * 1.2
            product.stock += quantity
            product.save()

            order_items.append(InvoiceItem(
                invoice=invoice,
                product=product,
                quantity=quantity,
                purchase_price=purchase_price
            ))

        InvoiceItem.objects.bulk_create(order_items)

        return Response(InvoiceSerializer(invoice).data, status=status.HTTP_201_CREATED)