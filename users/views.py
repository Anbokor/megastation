
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny

class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:  # Если администратор, показываем всех пользователей
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)  # Иначе только свой профиль

    permission_classes = [permissions.IsAuthenticated]  # Только авторизованные пользователи

class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = True  # Делаем пользователя активным сразу после регистрации
        user.save()
