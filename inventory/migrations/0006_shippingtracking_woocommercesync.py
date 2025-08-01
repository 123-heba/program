# Generated by Django 5.2.4 on 2025-07-18 10:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_expensecategory_revenuecategory_expense_revenue'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShippingTracking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(max_length=100, unique=True)),
                ('shipping_company', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('pending', 'في الانتظار'), ('processing', 'قيد المعالجة'), ('shipped', 'تم الشحن'), ('delivered', 'تم التسليم'), ('cancelled', 'ملغي')], default='pending', max_length=20)),
                ('estimated_delivery', models.DateTimeField(blank=True, null=True)),
                ('actual_delivery', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='inventory.order')),
            ],
            options={
                'verbose_name': 'تتبع الشحنة',
                'verbose_name_plural': 'تتبع الشحنات',
            },
        ),
        migrations.CreateModel(
            name='WooCommerceSync',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sync_type', models.CharField(choices=[('product', 'منتج'), ('customer', 'عميل'), ('order', 'طلب')], max_length=20)),
                ('local_id', models.IntegerField()),
                ('woocommerce_id', models.IntegerField()),
                ('last_sync', models.DateTimeField(auto_now=True)),
                ('sync_status', models.CharField(default='synced', max_length=20)),
            ],
            options={
                'verbose_name': 'مزامنة WooCommerce',
                'verbose_name_plural': 'مزامنات WooCommerce',
                'unique_together': {('sync_type', 'local_id')},
            },
        ),
    ]
