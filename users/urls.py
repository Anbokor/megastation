from django.urls import path
from .views import (
    UserListView, UserDetailView, UserRegisterView, LogoutView, LoginView, UserMeView, CustomerListView
)
from rest_framework_simplejwt.views import TokenRefreshView

app_name = "users"
urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("", UserListView.as_view(), name="user-list"),
    path("me/", UserMeView.as_view(), name="me"),
    path("<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("customers/", CustomerListView.as_view(), name="customer-list"),
]