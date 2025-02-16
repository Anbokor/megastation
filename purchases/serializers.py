from rest_framework import serializers
from .models import Invoice, InvoiceItem, InvoiceReturn
from store.models import Product
from inventory.models import SalesPoint


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]


class SalesPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPoint
        fields = ["id", "name"]


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = InvoiceItem
        fields = ["id", "invoice", "product", "product_id", "quantity", "cost_per_item", "total_cost"]

    def get_total_cost(self, obj):
        return obj.quantity * obj.cost_per_item


class InvoiceSerializer(serializers.ModelSerializer):
    sales_point = SalesPointSerializer(read_only=True)
    sales_point_id = serializers.PrimaryKeyRelatedField(
        queryset=SalesPoint.objects.all(), source="sales_point", write_only=True
    )
    items = InvoiceItemSerializer(many=True)
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["id", "invoice_number", "supplier", "sales_point", "sales_point_id", "status", "created_at", "total_cost", "items"]

    def get_total_cost(self, obj):
        return sum(item.quantity * item.cost_per_item for item in obj.items.all())

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Una factura debe contener al menos un artículo.")
        return value


class InvoiceReturnSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product", write_only=True
    )
    invoice = serializers.PrimaryKeyRelatedField(queryset=Invoice.objects.all())
    sales_point = SalesPointSerializer(read_only=True)
    sales_point_id = serializers.PrimaryKeyRelatedField(
        queryset=SalesPoint.objects.all(), source="sales_point", write_only=True
    )

    class Meta:
        model = InvoiceReturn
        fields = ["id", "invoice", "product", "product_id", "sales_point", "sales_point_id", "quantity", "reason", "created_at"]

    def validate(self, data):
        invoice = data.get("invoice")
        product = data.get("product")
        quantity = data.get("quantity")

        if invoice.status != "procesada":
            raise serializers.ValidationError({"invoice": "Solo se pueden devolver productos de facturas procesadas."})

        invoice_item = InvoiceItem.objects.filter(invoice=invoice, product=product).first()
        if not invoice_item:
            raise serializers.ValidationError({"product": "El producto no está en la factura."})

        if quantity > invoice_item.quantity:
            raise serializers.ValidationError({"quantity": "No se puede devolver más cantidad de la comprada."})

        return data
