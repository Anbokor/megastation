# Generated by Django 5.1.6 on 2025-02-15 18:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0008_invoicereturn'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='invoiceitem',
            options={'ordering': ['invoice'], 'verbose_name': 'Artículo en Factura', 'verbose_name_plural': 'Artículos en Factura'},
        ),
    ]
