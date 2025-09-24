from rest_framework import serializers
from django.db import transaction
from django.db.models import Sum
from .models import Invoice, InvoiceItem, InvoiceReturn
from store.models import Product
from inventory.models import SalesPoint, Stock
from inventory.serializers import SalesPointSerializer
from users.serializers import SimpleUserSerializer # Import SimpleUserSerializer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]

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
    # FIX: Use a nested serializer for the user to provide an object with username
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Invoice
        # FIX: Add 'user' to the fields list
        fields = ["id", "invoice_number", "supplier", "sales_point", "sales_point_id", "status", "created_at", "total_cost", "items", "user"]

    def get_total_cost(self, obj):
        return sum(item.quantity * item.cost_per_item for item in obj.items.all())

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("Una factura debe contener al menos un artículo.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        invoice = Invoice.objects.create(**validated_data)
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        instance.supplier = validated_data.get("supplier", instance.supplier)
        instance.sales_point = validated_data.get("sales_point", instance.sales_point)
        new_status = validated_data.get("status", instance.status)

        with transaction.atomic():
            if instance.status == "procesada" and new_status == "anulada":
                instance.revert_stock()
            instance.status = new_status
            instance.save()

            if items_data is not None:
                if instance.status == "procesada":
                    instance.revert_stock()
                instance.items.all().delete()
                for item_data in items_data:
                    InvoiceItem.objects.create(invoice=instance, **item_data)
                if instance.status == "procesada":
                    instance.update_stock()

        return instance

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
        sales_point = data.get("sales_point")

        if invoice.status != "procesada":
            raise serializers.ValidationError({"invoice": "Solo se pueden devolver productos de facturas procesadas."})

        invoice_item = InvoiceItem.objects.filter(invoice=invoice, product=product).first()
        if not invoice_item:
            raise serializers.ValidationError({"product": "El producto no está en la factura."})

        total_returned = invoice.returns.filter(product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0
        if total_returned + quantity > invoice_item.quantity:
            raise serializers.ValidationError({"quantity": f"No se puede devolver más de {invoice_item.quantity - total_returned} unidades."})

        stock = Stock.objects.filter(product=product, sales_point=sales_point).first()
        if not stock or stock.quantity < quantity:
            raise serializers.ValidationError({"quantity": "No hay suficiente stock disponible para devolver."})

        return data
