# Generated by Django 5.2.4 on 2025-07-13 11:40

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='اسم العميل')),
                ('phone', models.CharField(max_length=20, verbose_name='رقم الهاتف')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='البريد الإلكتروني')),
                ('address', models.TextField(blank=True, null=True, verbose_name='العنوان')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'عميل',
                'verbose_name_plural': 'العملاء',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='اسم المنتج')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='السعر')),
                ('quantity', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='الكمية في المخزن')),
                ('min_quantity', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(0)], verbose_name='الحد الأدنى للكمية')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'منتج',
                'verbose_name_plural': 'المنتجات',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='اسم المورد')),
                ('phone', models.CharField(max_length=20, verbose_name='رقم الهاتف')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='البريد الإلكتروني')),
                ('address', models.TextField(blank=True, null=True, verbose_name='العنوان')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
            ],
            options={
                'verbose_name': 'مورد',
                'verbose_name_plural': 'الموردين',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=50, unique=True, verbose_name='رقم الفاتورة')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الفاتورة')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='المبلغ الإجمالي')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='أنشئت بواسطة')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.supplier', verbose_name='المورد')),
            ],
            options={
                'verbose_name': 'فاتورة شراء',
                'verbose_name_plural': 'فواتير الشراء',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseInvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='الكمية')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='سعر الوحدة')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='السعر الإجمالي')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.purchaseinvoice', verbose_name='الفاتورة')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product', verbose_name='المنتج')),
            ],
            options={
                'verbose_name': 'عنصر فاتورة شراء',
                'verbose_name_plural': 'عناصر فواتير الشراء',
            },
        ),
        migrations.CreateModel(
            name='SaleInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=50, unique=True, verbose_name='رقم الفاتورة')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الفاتورة')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='المبلغ الإجمالي')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='أنشئت بواسطة')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.customer', verbose_name='العميل')),
            ],
            options={
                'verbose_name': 'فاتورة بيع',
                'verbose_name_plural': 'فواتير البيع',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='SaleInvoiceItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)], verbose_name='الكمية')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))], verbose_name='سعر الوحدة')),
                ('total_price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='السعر الإجمالي')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='inventory.saleinvoice', verbose_name='الفاتورة')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.product', verbose_name='المنتج')),
            ],
            options={
                'verbose_name': 'عنصر فاتورة بيع',
                'verbose_name_plural': 'عناصر فواتير البيع',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.supplier', verbose_name='المورد'),
        ),
    ]
