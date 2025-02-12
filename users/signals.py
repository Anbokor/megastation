from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    """
    ✅ Автоматически назначает группу в зависимости от роли.
    """
    if created:
        if instance.role == 'admin':
            group, _ = Group.objects.get_or_create(name='Administradores')
            instance.groups.add(group)
        elif instance.role == 'store_admin':
            group, _ = Group.objects.get_or_create(name='Administradores de Tienda')
            instance.groups.add(group)
        elif instance.role == 'seller':
            group, _ = Group.objects.get_or_create(name='Vendedores')
            instance.groups.add(group)
        elif instance.role == 'customer':
            group, _ = Group.objects.get_or_create(name='Clientes')
            instance.groups.add(group)
