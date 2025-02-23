from django.urls import path
from .views import UserListView, UserDetailView, UserRegisterView, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginView

app_name = "users"

urlpatterns = [
    path("", UserListView.as_view(), name="list"),  # ✅ Исправлено
    path("<int:pk>/", UserDetailView.as_view(), name="detail"),  # ✅ Исправлено
    path("register/", UserRegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="token_obtain_pair"),  # ✅ Теперь с защитой
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
