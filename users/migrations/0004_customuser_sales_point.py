# Generated by Django 5.1.6 on 2025-03-14 21:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_stock_sales_point'),
        ('users', '0003_alter_customuser_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='sales_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.salespoint', verbose_name='Punto de venta'),
        ),
    ]
