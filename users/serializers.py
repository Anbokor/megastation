from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    is_admin = serializers.BooleanField(source='is_admin', read_only=True)
    is_store_admin = serializers.BooleanField(source='is_store_admin', read_only=True)
    is_seller = serializers.BooleanField(source='is_seller', read_only=True)
    is_customer = serializers.BooleanField(source='is_customer', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role', 'password',
            'is_admin', 'is_store_admin', 'is_seller', 'is_customer'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        ✅ Автоматически назначает `customer` по умолчанию.
        ✅ Администратор может создать `store_admin` или `seller`.
        ✅ Обычные пользователи не могут выбирать роль.
        """
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or not request.user.is_admin():
            validated_data['role'] = 'customer'  # 🔥 Только админ может задать другую роль

        validated_data['password'] = make_password(validated_data['password'])  # ✅ Хешируем пароль
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        ✅ Блокируем изменение роли после создания.
        ✅ Обновляем только безопасные поля.
        """
        validated_data.pop('role', None)  # 🔥 Нельзя изменить роль
        return super().update(instance, validated_data)
