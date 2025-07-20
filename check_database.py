#!/usr/bin/env python3
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from django.contrib.auth.models import User
from inventory.models import *

def check_database():
    print("🔍 فحص قاعدة البيانات...")
    
    # التحقق من المستخدمين
    users_count = User.objects.count()
    print(f"✅ عدد المستخدمين: {users_count}")
    
    if users_count > 0:
        admin_users = User.objects.filter(is_superuser=True)
        print(f"✅ عدد المديرين: {admin_users.count()}")
        for admin in admin_users:
            print(f"   - {admin.username}")
    
    # التحقق من الجداول
    try:
        suppliers_count = Supplier.objects.count()
        print(f"✅ عدد الموردين: {suppliers_count}")
    except Exception as e:
        print(f"❌ خطأ في جدول الموردين: {e}")
    
    try:
        customers_count = Customer.objects.count()
        print(f"✅ عدد العملاء: {customers_count}")
    except Exception as e:
        print(f"❌ خطأ في جدول العملاء: {e}")
    
    try:
        products_count = Product.objects.count()
        print(f"✅ عدد المنتجات: {products_count}")
    except Exception as e:
        print(f"❌ خطأ في جدول المنتجات: {e}")
    
    print("\n🎉 فحص قاعدة البيانات مكتمل!")

if __name__ == "__main__":
    check_database()