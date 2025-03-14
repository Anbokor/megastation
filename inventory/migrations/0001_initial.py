# Generated by Django 5.1.6 on 2025-02-13 22:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0007_delete_stockmovement'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre del punto de venta')),
                ('administrators', models.ManyToManyField(related_name='managed_sales_points', to=settings.AUTH_USER_MODEL, verbose_name='Administradores')),
                ('sellers', models.ManyToManyField(related_name='sales_points', to=settings.AUTH_USER_MODEL, verbose_name='Vendedores')),
            ],
            options={
                'verbose_name': 'Punto de venta',
                'verbose_name_plural': 'Puntos de venta',
            },
        ),
        migrations.CreateModel(
            name='StockMovement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reason', models.CharField(max_length=255)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
                ('sales_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_movements', to='inventory.salespoint', verbose_name='Punto de venta')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('low_stock_threshold', models.PositiveIntegerField(default=5)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock_info', to='store.product')),
                ('sales_point', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='inventory.salespoint', verbose_name='Punto de venta')),
            ],
            options={
                'unique_together': {('product', 'sales_point')},
            },
        ),
    ]
