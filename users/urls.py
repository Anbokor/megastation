from django.urls import path
from .views import UserListView, UserDetailView, UserRegisterView, LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import LoginView
urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),  # ✅ Новый маршрут
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),  # ✅ Теперь с защитой
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
