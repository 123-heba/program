#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_urls():
    print("🔗 فحص الروابط...")
    
    client = Client()
    
    # الروابط العامة
    urls_to_test = [
        ('/', 'الصفحة الرئيسية'),
        ('/login/', 'صفحة تسجيل الدخول'),
    ]
    
    for url, name in urls_to_test:
        try:
            response = client.get(url)
            if response.status_code in [200, 302]:
                print(f"✅ {name}: {url} - {response.status_code}")
            else:
                print(f"❌ {name}: {url} - {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {url} - خطأ: {e}")
    
    # تسجيل الدخول واختبار الروابط المحمية
    try:
        user = User.objects.filter(is_superuser=True).first()
        if user:
            client.force_login(user)
            
            protected_urls = [
                ('/dashboard/', 'لوحة التحكم'),
                ('/suppliers/', 'الموردين'),
                ('/customers/', 'العملاء'),
                ('/products/', 'المنتجات'),
            ]
            
            for url, name in protected_urls:
                try:
                    response = client.get(url)
                    if response.status_code == 200:
                        print(f"✅ {name}: {url} - {response.status_code}")
                    else:
                        print(f"⚠️ {name}: {url} - {response.status_code}")
                except Exception as e:
                    print(f"❌ {name}: {url} - خطأ: {e}")
    except Exception as e:
        print(f"❌ خطأ في تسجيل الدخول: {e}")
    
    print("\n🎉 فحص الروابط مكتمل!")

if __name__ == "__main__":
    test_urls()