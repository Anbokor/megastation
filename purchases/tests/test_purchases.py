import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from purchases.models import Invoice, InvoiceItem, InvoiceReturn
from store.models import Product
from inventory.models import SalesPoint
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin():
    return CustomUser.objects.create_superuser(username='admin', password='admin123', email='admin@example.com')

@pytest.fixture
def product():
    # Use a unique barcode for each test run
    import uuid
    unique_barcode = f"123456789-{uuid.uuid4().hex[:8]}"
    return Product.objects.create(name="Laptop", price=1000, barcode=unique_barcode)

@pytest.fixture
def sales_point():
    return SalesPoint.objects.create(name="Main Store")

@pytest.fixture
def invoice(admin, sales_point, product):
    invoice = Invoice.objects.create(
        supplier="Tech Supplier",
        user=admin,
        sales_point=sales_point,
        status="pendiente"
    )
    InvoiceItem.objects.create(
        invoice=invoice,
        product=product,
        quantity=10,
        cost_per_item=100
    )
    return invoice

@pytest.mark.django_db
def test_create_invoice(api_client, admin, sales_point, product):
    """Test de creación de factura"""
    api_client.force_authenticate(admin)
    data = {
        "invoice_number": "INV-TEST-001",
        "supplier": "Tech Supplier",
        "sales_point": sales_point.id,
        "items": [{"product_id": product.id, "quantity": 5, "purchase_price": 100}]
    }
    response = api_client.post(reverse("invoice-create"), data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert Invoice.objects.count() == 1

@pytest.mark.django_db
def test_get_invoice_list(api_client, admin, invoice):
    """Test de obtención de lista de facturas"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_invoice_detail(api_client, admin, invoice):
    """Test de obtención de detalles de factura"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-detail", args=[invoice.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["invoice_number"] == invoice.invoice_number

@pytest.mark.django_db
def test_update_invoice_status(api_client, admin, invoice):
    """Test de actualización de estado de factura"""
    api_client.force_authenticate(admin)
    response = api_client.patch(reverse("invoice-update-status", args=[invoice.id]), {"status": "procesada"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    invoice.refresh_from_db()
    assert invoice.status == "procesada"

@pytest.fixture
def invoice_return(invoice, product, sales_point):
    invoice.status = "procesada"
    invoice.save()
    return InvoiceReturn.objects.create(
        invoice=invoice,
        product=product,
        sales_point=sales_point,
        quantity=5,
        reason="Producto defectuoso"
    )

@pytest.mark.django_db
def test_create_invoice_return(api_client, admin, invoice, product, sales_point):
    """Test de creación de devolución de factura"""
    invoice.status = "procesada"
    invoice.save()
    api_client.force_authenticate(admin)
    data = {
        "invoice_id": invoice.id,
        "product_id": product.id,
        "sales_point_id": sales_point.id,
        "quantity": 2,
        "reason": "Producto defectuoso"
    }
    response = api_client.post(reverse("invoice-returns-create"), data, format="json")
    assert response.status_code == status.HTTP_201_CREATED
    assert InvoiceReturn.objects.count() == 1

@pytest.mark.django_db
def test_get_invoice_returns(api_client, admin, invoice_return):
    """Test de obtención de lista de devoluciones"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-returns-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_invoice_return_detail(api_client, admin, invoice_return):
    """Test de obtención de detalles de devolución"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-returns-detail", args=[invoice_return.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["quantity"] == 5