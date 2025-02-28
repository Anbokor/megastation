from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        """
        ✅ Automatically sets role to 'customer' for all registrations via /api/register/.
        ✅ Администраторы могут создавать пользователей с другими ролями через другие эндпоинты.
        """
        request = self.context.get('request')
        is_admin_request = False

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            is_admin_request = request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == CustomUser.Role.ADMIN)
            logger.debug(f"Request user: {request.user}, is_authenticated: {request.user.is_authenticated}, is_superuser: {request.user.is_superuser}, role: {getattr(request.user, 'role', 'None')}")

        # Для неавторизованных пользователей или неадминов фиксируем роль customer
        validated_data['role'] = CustomUser.Role.CUSTOMER

        validated_data['password'] = make_password(validated_data['password'])  # Хешируем пароль
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.SerializerMethodField()
    is_store_admin = serializers.SerializerMethodField()
    is_seller = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'password',
            'is_admin', 'is_store_admin', 'is_seller', 'is_customer'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_admin(self, obj):
        return obj.is_admin

    def get_is_store_admin(self, obj):
        return obj.is_store_admin

    def get_is_seller(self, obj):
        return obj.is_seller

    def get_is_customer(self, obj):
        return obj.is_customer

    def create(self, validated_data):
        """
        ✅ Автоматически назначает `customer` по умолчанию для неадминов.
        ✅ Администратор (is_superuser или role=admin) может создать `store_admin` или `seller`.
        ✅ Обычные пользователи не могут выбирать роль.
        """
        request = self.context.get('request')
        is_admin_request = False

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            is_admin_request = request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == CustomUser.Role.ADMIN)

        if not is_admin_request:
            validated_data['role'] = CustomUser.Role.CUSTOMER  # Роль по умолчанию для неадминов
        else:
            # Если запрос от админа, используем роль из validated_data, если она указана
            role = validated_data.pop('role', CustomUser.Role.CUSTOMER)
            if role not in [CustomUser.Role.STORE_ADMIN, CustomUser.Role.SELLER, CustomUser.Role.CUSTOMER]:
                raise serializers.ValidationError({"role": "Role must be store_admin, seller, or customer."})
            validated_data['role'] = role

        validated_data['password'] = make_password(validated_data['password'])  # Хешируем пароль
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        ✅ Блокируем изменение роли после создания.
        ✅ Обновляем только безопасные поля.
        """
        validated_data.pop('role', None)  # Нельзя изменить роль
        return super().update(instance, validated_data)