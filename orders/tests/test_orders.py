import pytest
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.core import mail
from inventory.models import Stock, StockMovement, SalesPoint
from store.models import Product, Category
from cart.models import CartItem
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderItemSerializer
from orders.views import OrderListView, OrderDetailView, OrderCreateView, CancelOrderView, OrderUpdateView
from users.models import CustomUser

@pytest.fixture
def sales_point(db):
    return SalesPoint.objects.create(name="Main Warehouse")

@pytest.fixture
def category(db):
    return Category.objects.create(name="Electronics")

@pytest.fixture
def product(category, db):
    return Product.objects.create(name="Laptop", category=category, price=1000)

@pytest.fixture
def stock(product, sales_point, db):
    return Stock.objects.create(product=product, sales_point=sales_point, quantity=20, low_stock_threshold=5)

@pytest.fixture
def order(authenticated_client, product, stock, db):
    _, user = authenticated_client
    order = Order.objects.create(user=user, total_price=2000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=2)
    return order

# Тесты для моделей
@pytest.mark.django_db
def test_order_creation(authenticated_client):
    _, user = authenticated_client
    order = Order.objects.create(user=user, total_price=1500, status="pendiente")
    assert order.user == user
    assert order.total_price == 1500
    assert order.status == "pendiente"
    assert str(order).startswith(f"Orden {order.id} - {user.username}")

@pytest.mark.django_db
def test_order_item_creation(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=2000, status="pendiente")
    item = OrderItem.objects.create(order=order, product=product, quantity=3)
    stock.refresh_from_db()
    assert item.quantity == 3
    assert stock.quantity == 17
    assert stock.reserved_quantity == 3


@pytest.mark.django_db
def test_order_item_insufficient_stock(authenticated_client, product, sales_point):
    client, user = authenticated_client

    # 🔥 Создаем склад с резервом
    stock = Stock.objects.create(product=product, sales_point=sales_point, quantity=10, reserved_quantity=5)

    order = Order.objects.create(user=user, total_price=1000, status="pendiente")

    # Используем сериализатор, который вызовет валидацию
    data = {"order": order.id, "product": product.id, "quantity": 6}
    serializer = OrderItemSerializer(data=data)

    assert not serializer.is_valid()
    assert "stock" in serializer.errors
    assert "No hay suficiente stock disponible" in serializer.errors["stock"][0]  # ✅ Исправлено


@pytest.mark.django_db
def test_order_item_delete(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    item = OrderItem.objects.create(order=order, product=product, quantity=2)
    stock.refresh_from_db()
    assert stock.quantity == 18
    assert stock.reserved_quantity == 2
    item.delete()
    stock.refresh_from_db()
    assert stock.quantity == 20
    assert stock.reserved_quantity == 0

@pytest.mark.django_db
def test_order_update_status(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=2)
    stock.refresh_from_db()
    assert stock.quantity == 18
    assert stock.reserved_quantity == 2

    order.update_status("en_proceso")
    stock.refresh_from_db()
    assert stock.quantity == 18
    assert stock.reserved_quantity == 0

    order.update_status("cancelado")
    stock.refresh_from_db()
    assert stock.quantity == 20
    assert stock.reserved_quantity == 0

# Тесты для сериализаторов
@pytest.mark.django_db
def test_order_item_serializer(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=5000, status="pendiente")
    data = {"order": order.id, "product": product.id, "quantity": 5}
    serializer = OrderItemSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    item = serializer.save()
    stock.refresh_from_db()
    assert item.quantity == 5
    assert stock.quantity == 15
    assert stock.reserved_quantity == 5

@pytest.mark.django_db
def test_order_serializer(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=2)
    serializer = OrderSerializer(order)
    assert serializer.data["user"] == user.id
    assert serializer.data["total_price"] == "1000.00"
    assert len(serializer.data["items"]) == 1

@pytest.mark.django_db
def test_order_serializer_status_validation(authenticated_client, product, stock):
    client, user = authenticated_client
    user.is_staff = True
    user.save()
    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=2)
    serializer = OrderSerializer(order, data={"status": "en_proceso"}, context={"request": type("Request", (), {"user": user})()})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    assert order.status == "en_proceso"

# Тесты для представлений
@pytest.mark.django_db
def test_order_list_view_user(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=1)
    response = client.get("/api/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["user"] == user.id

@pytest.mark.django_db
def test_order_list_view_staff(authenticated_client, product, stock):
    client, user = authenticated_client
    user.is_staff = True
    user.save()
    order1 = Order.objects.create(user=user, total_price=1000, status="pendiente")
    order2 = Order.objects.create(user=user, total_price=2000, status="en_proceso")
    OrderItem.objects.create(order=order1, product=product, quantity=1)
    OrderItem.objects.create(order=order2, product=product, quantity=1)
    response = client.get("/api/orders/")
    assert response.status_code == 200
    assert len(response.json()) == 2

@pytest.mark.django_db
def test_order_detail_view(authenticated_client, product, stock):
    client, user = authenticated_client
    user.is_staff = True
    user.save()

    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=2)

    response = client.get(f"/api/orders/{order.id}/")
    assert response.status_code == 200

    print("📌 Stock перед отправкой:", stock.quantity)  # 🔥 Отладка

    response = client.patch(f"/api/orders/{order.id}/", {"status": "enviado"}, format="json")
    assert response.status_code == 200

    stock.refresh_from_db()
    print("📌 Stock после отправки:", stock.quantity)  # 🔥 Отладка

    assert stock.quantity == 18  # Нужно проверить, почему не 18

@pytest.mark.django_db
def test_order_create_view(authenticated_client, product, stock, sales_point):
    client, user = authenticated_client
    CartItem.objects.create(user=user, product=product, quantity=3)
    response = client.post("/api/orders/create/", {}, format="json")
    assert response.status_code == 201
    order = Order.objects.get(user=user)
    assert order.total_price == 3000
    assert order.items.count() == 1
    stock.refresh_from_db()
    assert stock.quantity == 17
    assert stock.reserved_quantity == 3
    movement = StockMovement.objects.get(product=product, change=-3)
    assert movement.sales_point == sales_point

@pytest.mark.django_db
def test_cancel_order_view(authenticated_client, product, stock):
    client, user = authenticated_client
    order = Order.objects.create(user=user, total_price=1000, status="pendiente")
    OrderItem.objects.create(order=order, product=product, quantity=2)
    stock.refresh_from_db()
    assert stock.quantity == 18
    assert stock.reserved_quantity == 2
    response = client.post(f"/api/orders/{order.id}/cancel/")
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "cancelado"
    stock.refresh_from_db()
    assert stock.quantity == 20
    assert stock.reserved_quantity == 0


@pytest.mark.django_db
def test_order_update_view(authenticated_client, product, stock):
    client, user = authenticated_client
    user.is_staff = True
    user.role = CustomUser.Role.ADMIN  # ✅ Теперь `CustomUser` доступен
    user.save()

    order = Order.objects.create(user=user, total_price=1000, status="pendiente")

    response = client.patch(f"/api/orders/{order.id}/", {"status": "enviado"}, format="json")
    assert response.status_code == 200