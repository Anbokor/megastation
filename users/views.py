from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import UserSerializer, UserRegisterSerializer
from .permissions import IsAdmin, IsSuperuser, IsStoreAdmin
from rest_framework.throttling import ScopedRateThrottle
from rest_framework import mixins
import logging
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

logger = logging.getLogger(__name__)

class UserListView(mixins.ListModelMixin, generics.GenericAPIView):
    """
    Admins see all users.
    Regular users see only their own profile.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user_list"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.is_superuser or user.role == CustomUser.Role.ADMIN:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=user.id)

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return Response({"error": "Método no permitido."}, status=405)

class UserRegisterView(generics.CreateAPIView):
    """
    Allows users to register with username, password, and email as customers only.
    Returns an access token for immediate login.
    """
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user_register"

    def perform_create(self, serializer):
        """
        Create a new user with active status and customer role.
        """
        user = serializer.save()
        user.is_active = True
        user.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = AccessToken.for_user(user)
        return Response({
            'user': serializer.data,
            'token': str(token)
        }, status=201)

class UserDetailView(APIView):
    """
    API for viewing and editing users.
    - Admins can view/edit any profile.
    - Regular users can edit only their own profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "user_list"

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if not request.user.is_staff and request.user != user:
            return Response({"error": "No tienes permiso para ver este perfil."}, status=403)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if not request.user.is_staff and request.user != user:
            return Response({"error": "No tienes permiso para editar este perfil."}, status=403)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """
        Only admins can delete users.
        """
        if not request.user.is_staff:
            return Response({"error": "No tienes permiso para eliminar este usuario."}, status=403)
        user = get_object_or_404(CustomUser, pk=pk)
        user.delete()
        return Response({"message": "Usuario eliminado correctamente"}, status=204)

class LogoutView(APIView):
    """
    API for logging out (blacklisting refresh token).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Token de actualización no proporcionado."}, status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Cierre de sesión exitoso."}, status=200)
        except TokenError:
            return Response({"error": "Token inválido o ya ha sido utilizado."}, status=400)

class LoginView(TokenObtainPairView):
    """
    API for logging in with logging.
    """
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login_attempt"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f"Usuario {request.data.get('username')} ha iniciado sesión exitosamente.")
        else:
            logger.warning(f"Intento fallido de inicio de sesión para {request.data.get('username')}.");
        return response

class UserMeView(APIView):
    """
    API for retrieving current user's data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class CustomerListView(generics.ListAPIView):
    """
    API to list all customers (role: 'customer').
    Accessible to superuser, admin, and store_admin.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, (IsSuperuser | IsAdmin | IsStoreAdmin)]

    def get_queryset(self):
        """
        Return only users with 'customer' role.
        """
        return CustomUser.objects.filter(role=CustomUser.Role.CUSTOMER)