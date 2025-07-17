from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('inventory', '0002_order_orderitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='اسم الصلاحية')),
                ('codename', models.CharField(max_length=100, unique=True, verbose_name='الرمز')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
            ],
            options={
                'verbose_name': 'صلاحية',
                'verbose_name_plural': 'الصلاحيات',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='اسم الدور')),
                ('description', models.TextField(blank=True, null=True, verbose_name='الوصف')),
                ('is_active', models.BooleanField(default=True, verbose_name='نشط')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('permissions', models.ManyToManyField(blank=True, related_name='roles', to='inventory.permission', verbose_name='الصلاحيات')),
            ],
            options={
                'verbose_name': 'دور وظيفي',
                'verbose_name_plural': 'الأدوار الوظيفية',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(max_length=20, unique=True, verbose_name='رقم الموظف')),
                ('department', models.CharField(blank=True, max_length=100, null=True, verbose_name='القسم')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='رقم الهاتف')),
                ('address', models.TextField(blank=True, null=True, verbose_name='العنوان')),
                ('hire_date', models.DateField(verbose_name='تاريخ التوظيف')),
                ('salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='الراتب')),
                ('employment_status', models.CharField(choices=[('active', 'نشط'), ('inactive', 'غير نشط'), ('suspended', 'موقوف'), ('terminated', 'منتهي الخدمة')], default='active', max_length=20, verbose_name='حالة التوظيف')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='ملاحظات')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.role', verbose_name='الدور الوظيفي')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_profile', to=settings.AUTH_USER_MODEL, verbose_name='المستخدم')),
            ],
            options={
                'verbose_name': 'موظف',
                'verbose_name_plural': 'الموظفين',
                'ordering': ['employee_id'],
            },
        ),
    ]
