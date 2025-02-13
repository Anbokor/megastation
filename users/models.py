from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador del sistema"
        STORE_ADMIN = "store_admin", "Administrador de tienda"
        SELLER = "seller", "Vendedor"
        CUSTOMER = "customer", "Cliente"

    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name="Rol"
    )

    @property
    def is_admin(self):
        return self.role == CustomUser.Role.ADMIN

    @property
    def is_store_admin(self):
        return self.role == CustomUser.Role.STORE_ADMIN

    @property
    def is_seller(self):
        return self.role == CustomUser.Role.SELLER

    @property
    def is_customer(self):
        return self.role == CustomUser.Role.CUSTOMER

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
