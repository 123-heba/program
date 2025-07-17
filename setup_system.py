#!/usr/bin/env python3
"""
سكريبت إعداد النظام
يقوم بإنشاء الصلاحيات والأدوار الأساسية
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from inventory.models import Employee, Role, Permission

def main():
    print("🚀 بدء إعداد النظام...")
    
    # 1. تطبيق migrations
    print("\n📦 تطبيق migrations...")
    try:
        call_command('makemigrations')
        call_command('migrate')
        print("✅ تم تطبيق migrations بنجاح")
    except Exception as e:
        print(f"❌ خطأ في migrations: {e}")
        return
    
    # 2. إنشاء الصلاحيات والأدوار
    print("\n🔐 إنشاء الصلاحيات والأدوار...")
    try:
        call_command('setup_permissions')
        print("✅ تم إنشاء الصلاحيات والأدوار بنجاح")
    except Exception as e:
        print(f"❌ خطأ في إنشاء الصلاحيات: {e}")
    
    # 3. إنشاء مدير عام إذا لم يكن موجود
    print("\n👤 التحقق من وجود مدير عام...")
    if not User.objects.filter(is_superuser=True).exists():
        print("إنشاء مدير عام جديد...")
        username = input("اسم المستخدم للمدير العام: ") or "admin"
        email = input("البريد الإلكتروني (اختياري): ") or ""
        password = input("كلمة المرور: ") or "admin123"
        
        admin_user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name="مدير",
            last_name="النظام"
        )
        print(f"✅ تم إنشاء المدير العام: {username}")
    else:
        print("✅ يوجد مدير عام بالفعل")
    
    # 4. إنشاء موظف تجريبي
    print("\n👥 إنشاء موظف تجريبي...")
    try:
        # التحقق من وجود دور "موظف"
        employee_role = Role.objects.filter(name="موظف").first()
        
        if not User.objects.filter(username="employee").exists():
            employee_user = User.objects.create_user(
                username="employee",
                password="employee123",
                first_name="موظف",
                last_name="تجريبي",
                email="employee@test.com"
            )
            
            if employee_role:
                Employee.objects.create(
                    user=employee_user,
                    role=employee_role,
                    department="قسم المبيعات",
                    hire_date="2024-01-01",
                    employment_status="active"
                )
            
            print("✅ تم إنشاء الموظف التجريبي: employee / employee123")
        else:
            print("✅ يوجد موظف تجريبي بالفعل")
            
    except Exception as e:
        print(f"⚠️ تحذير: لم يتم إنشاء الموظف التجريبي: {e}")
    
    print("\n🎉 تم إعداد النظام بنجاح!")
    print("\n📋 معلومات تسجيل الدخول:")
    print("=" * 40)
    print("المدير العام:")
    print(f"  اسم المستخدم: admin")
    print(f"  كلمة المرور: admin123")
    print("\nالموظف التجريبي:")
    print(f"  اسم المستخدم: employee")
    print(f"  كلمة المرور: employee123")
    print("=" * 40)
    print("\n🚀 يمكنك الآن تشغيل الخادم:")
    print("python manage.py runserver")

if __name__ == "__main__":
    main()
