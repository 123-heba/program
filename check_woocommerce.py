#!/usr/bin/env python3
import os
import django
import requests
from requests.auth import HTTPBasicAuth

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory_system.settings')
django.setup()

from django.conf import settings

def check_woocommerce_api():
    print("🔍 فحص إعدادات WooCommerce API...")
    print("=" * 50)
    
    # 1. فحص الإعدادات المحلية
    api_url = getattr(settings, 'WOOCOMMERCE_API_URL', '')
    consumer_key = getattr(settings, 'WOOCOMMERCE_CONSUMER_KEY', '')
    consumer_secret = getattr(settings, 'WOOCOMMERCE_CONSUMER_SECRET', '')
    
    print(f"🌐 API URL: {api_url}")
    print(f"🔑 Consumer Key: {consumer_key[:20]}..." if consumer_key else "❌ Consumer Key غير موجود")
    print(f"🔐 Consumer Secret: {consumer_secret[:20]}..." if consumer_secret else "❌ Consumer Secret غير موجود")
    
    if not all([api_url, consumer_key, consumer_secret]):
        print("\n❌ الإعدادات غير مكتملة!")
        print("\n📋 تحتاج إلى:")
        print("1. تحديث WOOCOMMERCE_API_URL برابط متجرك")
        print("2. التأكد من صحة Consumer Key")
        print("3. التأكد من صحة Consumer Secret")
        return False
    
    # 2. اختبار الاتصال
    print(f"\n🔗 اختبار الاتصال بـ {api_url}...")
    
    try:
        # تجربة جلب معلومات المتجر
        test_url = api_url.replace('/wp-json/wc/v3/', '/wp-json/wc/v3/system_status')
        
        response = requests.get(
            test_url,
            auth=HTTPBasicAuth(consumer_key, consumer_secret),
            timeout=10
        )
        
        print(f"📡 Response Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ الاتصال ناجح!")
            
            # تجربة جلب المنتجات
            products_url = api_url + "products"
            products_response = requests.get(
                products_url,
                auth=HTTPBasicAuth(consumer_key, consumer_secret),
                params={"per_page": 5},
                timeout=10
            )
            
            if products_response.status_code == 200:
                products = products_response.json()
                print(f"📦 عدد المنتجات المتاحة: {len(products)}")
                
                if products:
                    print("\n📋 أول 3 منتجات:")
                    for i, product in enumerate(products[:3]):
                        print(f"   {i+1}. {product.get('name', 'بدون اسم')} - {product.get('price', '0')} ريال")
                else:
                    print("⚠️ لا توجد منتجات في المتجر")
                
                return True
            else:
                print(f"❌ خطأ في جلب المنتجات: {products_response.status_code}")
                print(f"📄 Response: {products_response.text[:200]}...")
                
        elif response.status_code == 401:
            print("❌ خطأ في المصادقة!")
            print("🔧 تحقق من:")
            print("   - صحة Consumer Key و Consumer Secret")
            print("   - تفعيل REST API في WooCommerce")
            print("   - صلاحيات المستخدم")
            
        elif response.status_code == 404:
            print("❌ الرابط غير صحيح!")
            print("🔧 تحقق من:")
            print("   - صحة رابط المتجر")
            print("   - تثبيت WooCommerce")
            print("   - تفعيل REST API")
            
        else:
            print(f"❌ خطأ غير متوقع: {response.status_code}")
            print(f"📄 Response: {response.text[:200]}...")
            
    except requests.exceptions.Timeout:
        print("❌ انتهت مهلة الاتصال!")
        print("🔧 تحقق من الاتصال بالإنترنت ورابط المتجر")
        
    except requests.exceptions.ConnectionError:
        print("❌ فشل الاتصال!")
        print("🔧 تحقق من:")
        print("   - الاتصال بالإنترنت")
        print("   - صحة رابط المتجر")
        print("   - أن المتجر يعمل")
        
    except Exception as e:
        print(f"❌ خطأ غير متوقع: {e}")
    
    return False

def show_setup_guide():
    print("\n" + "=" * 50)
    print("📚 دليل إعداد WooCommerce REST API")
    print("=" * 50)
    
    print("\n1️⃣ تفعيل REST API:")
    print("   - اذهب إلى لوحة تحكم WooCommerce")
    print("   - WooCommerce → Settings → Advanced → REST API")
    print("   - تأكد من تفعيل REST API")
    
    print("\n2️⃣ إنشاء API Keys:")
    print("   - اضغط 'Add Key'")
    print("   - Description: 'Inventory Management'")
    print("   - User: اختر مستخدم إداري")
    print("   - Permissions: 'Read/Write'")
    print("   - اضغط 'Generate API Key'")
    
    print("\n3️⃣ تحديث الإعدادات:")
    print("   - انسخ Consumer Key و Consumer Secret")
    print("   - حدث ملف settings.py:")
    print("     WOOCOMMERCE_API_URL = 'https://your-store.com/wp-json/wc/v3/'")
    print("     WOOCOMMERCE_CONSUMER_KEY = 'your_key'")
    print("     WOOCOMMERCE_CONSUMER_SECRET = 'your_secret'")
    
    print("\n4️⃣ اختبار الاتصال:")
    print("   - شغل هذا السكريبت مرة أخرى")
    print("   - أو استخدم صفحة المزامنة في النظام")

if __name__ == "__main__":
    success = check_woocommerce_api()
    
    if not success:
        show_setup_guide()
    else:
        print("\n🎉 WooCommerce API جاهز للاستخدام!")
        print("💡 يمكنك الآن تشغيل المزامنة من:")
        print("   http://localhost:8000/woocommerce/sync/")