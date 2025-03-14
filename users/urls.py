from django.urls import path
from .views import UserListView, UserDetailView, UserRegisterView, LogoutView, UserMeView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginView

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="list"),
    path("<int:pk>/", UserDetailView.as_view(), name="detail"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserMeView.as_view(), name="me"),
]