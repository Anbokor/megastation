from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador del sistema'),
        ('store_admin', 'Administrador de tienda'),
        ('seller', 'Vendedor'),
        ('customer', 'Cliente'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer', verbose_name="Rol")

    def is_admin(self):
        return self.role == 'admin'

    def is_store_admin(self):
        return self.role == 'store_admin'

    def is_seller(self):
        return self.role == 'seller'

    def is_customer(self):
        return self.role == 'customer'

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
