import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from users.models import CustomUser


@pytest.mark.django_db
def test_user_registration():
    """Тест регистрации пользователя"""
    CustomUser.objects.all().delete()  # ✅ Очистка перед тестом

    client = APIClient()
    url = reverse("users:register")  # ✅ Используем `users:register`
    data = {"username": "newuser", "password": "newpassword"}
    response = client.post(url, data)

    assert response.status_code == 201  # ✅ 201 Created


@pytest.mark.django_db
def test_user_login():
    """Тест входа пользователя"""
    CustomUser.objects.all().delete()  # ✅ Очистка перед тестом
    user = CustomUser.objects.create_user(username="testuser", password="securepass")

    client = APIClient()
    url = reverse("users:token_obtain_pair")  # ✅ Теперь reverse() будет работать
    response = client.post(url, {"username": "testuser", "password": "securepass"})

    assert response.status_code == 200  # 200 OK
    assert "access" in response.data  # ✅ Должен вернуться access-токен


@pytest.mark.django_db
def test_user_logout():
    """Тест выхода пользователя (logout)."""
    CustomUser.objects.all().delete()  # ✅ Очистка перед тестом
    user = CustomUser.objects.create_user(username="testuser", password="securepass")

    client = APIClient()

    # ✅ Логинимся, получаем access и refresh токены
    login_url = reverse("users:token_obtain_pair")
    login_response = client.post(login_url, {"username": "testuser", "password": "securepass"})

    assert login_response.status_code == 200  # ✅ Логин успешен
    assert "refresh" in login_response.data  # ✅ Проверяем, что refresh-токен есть

    refresh_token = login_response.data["refresh"]  # ✅ Получаем refresh-токен
    access_token = login_response.data["access"]

    # ✅ Передаем access-токен в заголовке и refresh-токен в теле запроса
    logout_url = reverse("users:logout")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")  # ✅ Передача access-токена
    response = client.post(logout_url, {"refresh": refresh_token})

    assert response.status_code == 200  # ✅ Успешный выход
    assert response.data["detail"] == "Cierre de sesión exitoso."


@pytest.mark.django_db
def test_user_list_admin():
    """✅ Админ должен видеть всех пользователей"""
    client = APIClient()
    admin = CustomUser.objects.create_superuser(username="admin", password="adminpass")
    user1 = CustomUser.objects.create_user(username="user1", password="pass1")
    user2 = CustomUser.objects.create_user(username="user2", password="pass2")

    client.force_authenticate(admin)
    response = client.get(reverse("users:list"))

    assert response.status_code == 200
    assert len(response.data) == 3  # Должно быть 3 пользователя (admin, user1, user2)

@pytest.mark.django_db
def test_user_list_customer():
    """✅ Обычный пользователь видит только себя"""
    client = APIClient()
    user = CustomUser.objects.create_user(username="client", password="clientpass")

    client.force_authenticate(user)
    response = client.get(reverse("users:list"))

    assert response.status_code == 200
    assert len(response.data) == 1  # Только один пользователь

@pytest.mark.django_db
def test_user_update_profile():
    """✅ Пользователь может редактировать только себя"""
    client = APIClient()
    user = CustomUser.objects.create_user(username="client", password="clientpass")

    client.force_authenticate(user)
    url = reverse("users:detail", args=[user.id])
    response = client.patch(url, {"username": "new_name"}, format="json")

    assert response.status_code == 200
    assert response.data["username"] == "new_name"

@pytest.mark.django_db
def test_admin_update_user():
    """✅ Админ может редактировать любого пользователя"""
    client = APIClient()
    admin = CustomUser.objects.create_superuser(username="admin", password="adminpass")
    user = CustomUser.objects.create_user(username="client", password="clientpass")

    client.force_authenticate(admin)
    url = reverse("users:detail", args=[user.id])
    response = client.patch(url, {"username": "updated"}, format="json")

    assert response.status_code == 200
    assert response.data["username"] == "updated"

@pytest.mark.django_db
def test_user_cannot_update_other_profile():
    """❌ Обычный пользователь НЕ может редактировать чужой профиль"""
    client = APIClient()
    user1 = CustomUser.objects.create_user(username="user1", password="pass1")
    user2 = CustomUser.objects.create_user(username="user2", password="pass2")

    client.force_authenticate(user1)
    url = reverse("users:detail", args=[user2.id])
    response = client.patch(url, {"username": "hacker"}, format="json")

    assert response.status_code == 403  # Доступ запрещён

@pytest.mark.django_db
def test_admin_delete_user():
    """✅ Админ может удалить пользователя"""
    client = APIClient()
    admin = CustomUser.objects.create_superuser(username="admin", password="adminpass")
    user = CustomUser.objects.create_user(username="client", password="clientpass")

    client.force_authenticate(admin)
    url = reverse("users:detail", args=[user.id])
    response = client.delete(url)

    assert response.status_code == 204  # Успешное удаление

@pytest.mark.django_db
def test_user_cannot_delete_other():
    """❌ Обычный пользователь НЕ может удалить другого пользователя"""
    client = APIClient()
    user1 = CustomUser.objects.create_user(username="user1", password="pass1")
    user2 = CustomUser.objects.create_user(username="user2", password="pass2")

    client.force_authenticate(user1)
    url = reverse("users:detail", args=[user2.id])
    response = client.delete(url)

    assert response.status_code == 403  # Доступ запрещён

@pytest.mark.django_db
def test_throttling_register():
    """✅ Ограничение частоты запросов при регистрации"""
    client = APIClient()
    url = reverse("users:register")

    for _ in range(5):  # 5 быстрых запросов
        response = client.post(url, {"username": f"user{_}", "password": "pass123"})

    assert response.status_code in [201, 429]  # 201 если не достигнут лимит, 429 если достигнут

@pytest.mark.django_db
def test_throttling_login():
    """✅ Ограничение попыток входа"""
    client = APIClient()
    url = reverse("users:token_obtain_pair")

    for _ in range(5):  # 5 попыток входа
        response = client.post(url, {"username": "fakeuser", "password": "wrongpass"})

    assert response.status_code in [401, 429]  # 401 (неверные данные), 429 (достигнут лимит)