from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = "superuser", "Superusuario"
        ADMIN = "admin", "Administrador"
        STORE_ADMIN = "store_admin", "Administrador de tienda"
        SELLER = "seller", "Vendedor de tienda"
        CUSTOMER = "customer", "Cliente"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name="Rol")
    sales_point = models.ForeignKey('inventory.SalesPoint', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Punto de venta")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    def has_perm(self, perm, obj=None):
        if self.role == self.Role.SUPERUSER:
            return True
        if self.role == self.Role.ADMIN:
            return perm in ['add_user', 'change_user', 'delete_user', 'view_analytics']
        if self.role == self.Role.STORE_ADMIN and self.sales_point:
            return perm in ['change_stock', 'view_store']
        if self.role == self.Role.SELLER and self.sales_point:
            return perm in ['view_store', 'process_order']
        return self.role == self.Role.CUSTOMER