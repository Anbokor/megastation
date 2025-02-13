from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import UserSerializer
from .permissions import IsAdmin


class UserListView(generics.ListAPIView):
    """
    ✅ Администратор видит всех пользователей.
    ✅ Обычные пользователи видят только свой профиль.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", None) == CustomUser.Role.ADMIN:  # ✅ Проверка через `getattr`
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)  # Обычный пользователь видит только себя


class UserRegisterView(generics.CreateAPIView):
    """
    ✅ Регистрация нового пользователя.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        """
        ✅ Создаём нового пользователя с активным статусом.
        """
        user = serializer.save()
        user.is_active = True
        user.save()


class UserDetailView(APIView):
    """
    ✅ API для просмотра и редактирования пользователей (ТОЛЬКО АДМИН).
    """
    permission_classes = [IsAdmin]

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response({"message": "Usuario eliminado correctamente"}, status=204)


class LogoutView(APIView):
    """
    ✅ API для выхода (деактивации токена refresh).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Token de actualización no proporcionado."}, status=400)
            token = RefreshToken(refresh_token)
            token.blacklist()  # Добавляем в черный список (если включена поддержка)
            return Response({"detail": "Cierre de sesión exitoso."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
