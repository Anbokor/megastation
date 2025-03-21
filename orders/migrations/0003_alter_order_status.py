# Generated by Django 5.1.6 on 2025-02-12 01:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_alter_order_options_alter_orderitem_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En proceso'), ('enviado', 'Enviado'), ('cancelado', 'Cancelado')], default='pendiente', max_length=20, verbose_name='Estado'),
        ),
    ]
