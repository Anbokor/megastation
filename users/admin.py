from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from inventory.models import SalesPoint

class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "sales_point")
    list_filter = ("role", "sales_point")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email")}),
        ("Permisos", {"fields": ("role", "sales_point")}),
    )

    def get_queryset(self, request):
        if not request.user.has_perm('change_user'):
            return CustomUser.objects.filter(role__in=['store_admin', 'seller', 'customer'])
        return CustomUser.objects.all()

admin.site.register(CustomUser, CustomUserAdmin)