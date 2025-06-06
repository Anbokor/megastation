# Generated by Django 5.1.6 on 2025-02-22 22:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='reserved_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='stock',
            name='sales_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='inventory.salespoint', verbose_name='Punto de venta'),
        ),
    ]
