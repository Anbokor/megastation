import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from cart.models import CartItem
from store.models import Product, Category
from inventory.models import Stock, SalesPoint

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def product(db):
    category = Category.objects.create(name="Smartphones")
    return Product.objects.create(name="iPhone 15", category=category, price=1200)


@pytest.fixture
def stock(db, product):
    """
    ✅ Создаём товарный запас на складе для тестов.
    """
    sales_point = SalesPoint.objects.create(name="Main Warehouse")
    return Stock.objects.create(product=product, sales_point=sales_point, quantity=10)


@pytest.fixture
def cart_item(db, user, product, stock):
    """
    ✅ Создаём тестовый элемент корзины.
    """
    return CartItem.objects.create(user=user, product=product, quantity=2)


@pytest.mark.django_db
def test_add_to_cart(api_client, user, product, stock):
    """
    ✅ Проверяет добавление товара в корзину.
    """
    api_client.force_authenticate(user)
    data = {"product": product.id, "quantity": 3}
    response = api_client.post("/api/cart/", data, format="json")

    assert response.status_code == 201
    assert CartItem.objects.count() == 1
    cart_item = CartItem.objects.first()
    assert cart_item.quantity == 3
    assert cart_item.product == product


@pytest.mark.django_db
def test_get_cart_list(api_client, user, cart_item):
    """
    ✅ Проверяет получение списка товаров в корзине.
    """
    api_client.force_authenticate(user)
    response = api_client.get("/api/cart/")
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["product"] == cart_item.product.id


@pytest.mark.django_db
def test_get_cart_item(api_client, user, cart_item):
    """
    ✅ Проверяет получение одного элемента корзины.
    """
    api_client.force_authenticate(user)
    response = api_client.get(f"/api/cart/{cart_item.id}/")
    assert response.status_code == 200
    assert response.data["quantity"] == 2


@pytest.mark.django_db
def test_update_cart_item(api_client, user, cart_item):
    """
    ✅ Проверяет обновление количества товара в корзине.
    """
    api_client.force_authenticate(user)
    data = {"quantity": 5}
    response = api_client.patch(f"/api/cart/{cart_item.id}/", data, format="json")
    assert response.status_code == 200
    cart_item.refresh_from_db()
    assert cart_item.quantity == 5


@pytest.mark.django_db
def test_delete_cart_item(api_client, user, cart_item):
    """
    ✅ Проверяет удаление товара из корзины.
    """
    api_client.force_authenticate(user)
    response = api_client.delete(f"/api/cart/{cart_item.id}/")
    assert response.status_code == 204
    assert not CartItem.objects.filter(id=cart_item.id).exists()
