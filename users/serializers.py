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
        Automatically sets role to 'customer' for all registrations via /api/register/.
        Administrators can create users with other roles via other endpoints.
        """
        request = self.context.get('request')
        is_admin_request = False

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            is_admin_request = request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == CustomUser.Role.ADMIN)
            logger.debug(f"Request user: {request.user}, is_authenticated: {request.user.is_authenticated}, is_superuser: {request.user.is_superuser}, role: {getattr(request.user, 'role', 'None')}")

        validated_data['role'] = CustomUser.Role.CUSTOMER
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Automatically sets 'customer' role by default for non-admins.
        Administrators (superuser or role=admin) can create 'store_admin' or 'seller'.
        Regular users cannot choose role.
        """
        request = self.context.get('request')
        is_admin_request = False

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            is_admin_request = request.user.is_superuser or (hasattr(request.user, 'role') and request.user.role == CustomUser.Role.ADMIN)

        if not is_admin_request:
            validated_data['role'] = CustomUser.Role.CUSTOMER
        else:
            role = validated_data.pop('role', CustomUser.Role.CUSTOMER)
            if role not in [CustomUser.Role.STORE_ADMIN, CustomUser.Role.SELLER, CustomUser.Role.CUSTOMER]:
                raise serializers.ValidationError({"role": "Role must be store_admin, seller, or customer."})
            validated_data['role'] = role

        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Blocks role changes after creation.
        Updates only safe fields.
        """
        validated_data.pop('role', None)
        return super().update(instance, validated_data)