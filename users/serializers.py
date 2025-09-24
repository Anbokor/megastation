from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser
import logging

logger = logging.getLogger(__name__)

class SimpleUserSerializer(serializers.ModelSerializer):
    """A simple serializer for read-only representation of a user."""
    # Explicitly define the email field to ensure it's always included.
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        # This serializer is for public registration, so role is always customer.
        validated_data['role'] = CustomUser.Role.CUSTOMER
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    # Define role hierarchy weights. Lower number is higher privilege.
    ROLE_HIERARCHY = {
        CustomUser.Role.SUPERUSER: 0,
        CustomUser.Role.ADMIN: 1,
        CustomUser.Role.STORE_ADMIN: 2,
        CustomUser.Role.SELLER: 3,
        CustomUser.Role.CUSTOMER: 4,
    }

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'password', 'is_active', 'sales_point']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
        }

    def validate(self, data):
        # This validation logic should not run in a read-only context.
        # It requires the request in the context, which is not passed to nested serializers by default.
        if self.context.get('request') and self.context['request'].method != 'GET':
            requesting_user = self.context['request'].user
            target_user = self.instance
            target_role = data.get('role')

            # Superuser can do anything.
            if requesting_user.is_superuser:
                return data

            requesting_user_level = self.ROLE_HIERARCHY.get(requesting_user.role, 99)

            # On user update (self.instance exists)
            if target_user:
                target_user_level = self.ROLE_HIERARCHY.get(target_user.role, 99)
                # Rule: Prevent editing users of the same or higher level.
                if target_user_level <= requesting_user_level:
                    raise serializers.ValidationError("No puedes editar un usuario con un rol igual o superior al tuyo.")

            # On role assignment (create or update)
            if target_role:
                target_role_level = self.ROLE_HIERARCHY.get(target_role, 99)
                # Rule: Prevent assigning a role equal to or higher than one's own.
                if target_role_level <= requesting_user_level:
                    raise serializers.ValidationError("No puedes asignar un rol igual o superior al tuyo.")

        return data

    def create(self, validated_data):
        # The `validate` method already checked permissions.
        # We just need to hash the password.
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # The `validate` method already checked permissions.
        # Handle password update separately.
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        return super().update(instance, validated_data)
