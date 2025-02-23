import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from purchases.models import Invoice, InvoiceItem, InvoiceReturn
from store.models import Product
from inventory.models import SalesPoint, Stock
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="password")

@pytest.fixture
def admin():
    return User.objects.create_superuser(username="admin", password="adminpassword")

@pytest.fixture
def sales_point():
    return SalesPoint.objects.create(name="Main Store")

@pytest.fixture
def product():
    return Product.objects.create(name="Laptop", price=1000)

@pytest.fixture
def stock(sales_point, product):
    return Stock.objects.create(product=product, sales_point=sales_point, quantity=50)

@pytest.fixture
def invoice(admin, sales_point):
    return Invoice.objects.create(
        supplier="Tech Supplier",
        user=admin,
        sales_point=sales_point,
        status="pendiente"
    )

@pytest.fixture
def invoice_item(invoice, product):
    return InvoiceItem.objects.create(invoice=invoice, product=product, quantity=10, cost_per_item=900)

@pytest.fixture
def invoice_return(invoice, product, sales_point):
    invoice.status = "procesada"
    invoice.save()
    return InvoiceReturn.objects.create(invoice=invoice, product=product, sales_point=sales_point, quantity=2, reason="Defective")

@pytest.mark.django_db
def test_create_invoice(api_client, admin, sales_point, product):
    """✅ Тест создания накладной"""
    api_client.force_authenticate(admin)
    data = {
        "invoice_number": "INV-TEST-001",
        "supplier": "Tech Supplier",
        "sales_point": sales_point.id,
        "items": [
            {
                "product_id": product.id,
                "quantity": 5,
                "purchase_price": 900
            }
        ]
    }
    response = api_client.post(reverse("invoice-create"), data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_get_invoice_list(api_client, admin, invoice):
    """✅ Тест получения списка накладных"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_invoice_detail(api_client, admin, invoice):
    """✅ Тест получения деталей накладной"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-detail", args=[invoice.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["supplier"] == "Tech Supplier"

@pytest.mark.django_db
def test_update_invoice_status(api_client, admin, invoice):
    """✅ Тест обновления статуса накладной"""
    api_client.force_authenticate(admin)
    response = api_client.patch(reverse("invoice-update-status", args=[invoice.id]), {"status": "procesada"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    invoice.refresh_from_db()
    assert invoice.status == "procesada"

@pytest.mark.django_db
def test_create_invoice_return(api_client, admin, invoice, product, sales_point):
    """✅ Тест создания возврата товара по накладной"""
    invoice.status = "procesada"
    invoice.save()
    InvoiceItem.objects.create(invoice=invoice, product=product, quantity=10, cost_per_item=900)
    Stock.objects.create(product=product, sales_point=sales_point, quantity=10)

    api_client.force_authenticate(admin)
    data = {
        "invoice_id": invoice.id,
        "product_id": product.id,
        "sales_point_id": sales_point.id,
        "quantity": 3,
        "reason": "Damaged"
    }
    response = api_client.post(reverse("invoice-returns-create"), data, format="json")
    assert response.status_code == status.HTTP_201_CREATED

@pytest.mark.django_db
def test_get_invoice_returns(api_client, admin, invoice_return):
    """✅ Тест получения списка возвратов"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-returns-list"))
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1

@pytest.mark.django_db
def test_get_invoice_return_detail(api_client, admin, invoice_return):
    """✅ Тест получения деталей возврата"""
    api_client.force_authenticate(admin)
    response = api_client.get(reverse("invoice-returns-detail", args=[invoice_return.id]))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["quantity"] == 2