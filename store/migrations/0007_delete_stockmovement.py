# Generated by Django 5.1.6 on 2025-02-13 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_remove_product_stock'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StockMovement',
        ),
    ]
