from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from inventory.models import Permission, Role, Employee
from inventory.decorators import SYSTEM_PERMISSIONS


class Command(BaseCommand):
    help = 'إنشاء الصلاحيات والأدوار الأساسية للنظام'

    def handle(self, *args, **options):
        self.stdout.write('بدء إنشاء الصلاحيات والأدوار...')

        # إنشاء الصلاحيات
        self.create_permissions()
        
        # إنشاء الأدوار
        self.create_roles()
        
        self.stdout.write(
            self.style.SUCCESS('تم إنشاء الصلاحيات والأدوار بنجاح!')
        )

    def create_permissions(self):
        """إنشاء جميع الصلاحيات"""
        self.stdout.write('إنشاء الصلاحيات...')
        
        for codename, name in SYSTEM_PERMISSIONS.items():
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': name,
                    'description': f'صلاحية {name}'
                }
            )
            if created:
                self.stdout.write(f'  ✓ تم إنشاء صلاحية: {name}')
            else:
                self.stdout.write(f'  - موجودة بالفعل: {name}')

    def create_roles(self):
        """إنشاء الأدوار الأساسية"""
        self.stdout.write('إنشاء الأدوار...')

        # دور المدير العام
        manager_role, created = Role.objects.get_or_create(
            name='مدير عام',
            defaults={
                'description': 'مدير عام له صلاحيات كاملة في النظام',
                'is_active': True
            }
        )
        if created:
            # إضافة جميع الصلاحيات للمدير العام
            all_permissions = Permission.objects.all()
            manager_role.permissions.set(all_permissions)
            self.stdout.write('  ✓ تم إنشاء دور: مدير عام')
        else:
            self.stdout.write('  - موجود بالفعل: مدير عام')

        # دور مدير المبيعات
        sales_manager_role, created = Role.objects.get_or_create(
            name='مدير مبيعات',
            defaults={
                'description': 'مدير مبيعات مسؤول عن إدارة المبيعات والعملاء',
                'is_active': True
            }
        )
        if created:
            sales_permissions = Permission.objects.filter(
                codename__in=[
                    'view_customers', 'add_customers', 'edit_customers',
                    'view_sale_invoices', 'add_sale_invoices', 'edit_sale_invoices',
                    'view_orders', 'add_orders', 'edit_orders', 'process_orders',
                    'view_products', 'view_reports'
                ]
            )
            sales_manager_role.permissions.set(sales_permissions)
            self.stdout.write('  ✓ تم إنشاء دور: مدير مبيعات')
        else:
            self.stdout.write('  - موجود بالفعل: مدير مبيعات')

        # دور مدير المخزون
        inventory_manager_role, created = Role.objects.get_or_create(
            name='مدير مخزون',
            defaults={
                'description': 'مدير مخزون مسؤول عن إدارة المنتجات والموردين',
                'is_active': True
            }
        )
        if created:
            inventory_permissions = Permission.objects.filter(
                codename__in=[
                    'view_products', 'add_products', 'edit_products',
                    'view_suppliers', 'add_suppliers', 'edit_suppliers',
                    'view_purchase_invoices', 'add_purchase_invoices', 'edit_purchase_invoices',
                    'view_reports'
                ]
            )
            inventory_manager_role.permissions.set(inventory_permissions)
            self.stdout.write('  ✓ تم إنشاء دور: مدير مخزون')
        else:
            self.stdout.write('  - موجود بالفعل: مدير مخزون')

        # دور المحاسب
        accountant_role, created = Role.objects.get_or_create(
            name='محاسب',
            defaults={
                'description': 'محاسب مسؤول عن المراجعة المالية والتقارير',
                'is_active': True
            }
        )
        if created:
            accountant_permissions = Permission.objects.filter(
                codename__in=[
                    'view_sale_invoices', 'view_purchase_invoices',
                    'view_reports', 'export_data',
                    'view_products', 'view_customers', 'view_suppliers'
                ]
            )
            accountant_role.permissions.set(accountant_permissions)
            self.stdout.write('  ✓ تم إنشاء دور: محاسب')
        else:
            self.stdout.write('  - موجود بالفعل: محاسب')

        # دور الموظف العادي
        employee_role, created = Role.objects.get_or_create(
            name='موظف',
            defaults={
                'description': 'موظف عادي بصلاحيات محدودة',
                'is_active': True
            }
        )
        if created:
            employee_permissions = Permission.objects.filter(
                codename__in=[
                    'view_products', 'view_customers',
                    'view_sale_invoices', 'add_sale_invoices',
                    'view_orders', 'add_orders'
                ]
            )
            employee_role.permissions.set(employee_permissions)
            self.stdout.write('  ✓ تم إنشاء دور: موظف')
        else:
            self.stdout.write('  - موجود بالفعل: موظف')

        # إضافة صلاحيات إدارة الموظفين للمدير العام فقط
        manage_employees_permission = Permission.objects.filter(
            codename__in=['manage_employees', 'manage_roles']
        )
        manager_role.permissions.add(*manage_employees_permission)
