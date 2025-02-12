from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_superuser")
    list_filter = ("role", "is_staff")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email")}),
        ("Permisos", {"fields": ("role", "is_staff", "is_superuser", "groups")}),
    )

    def get_queryset(self, request):
        """
        ✅ Ограничивает доступ, чтобы продавцы не могли видеть других пользователей.
        """
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(role__in=['store_admin', 'seller', 'customer'])
        return qs

admin.site.register(CustomUser, CustomUserAdmin)
