from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import CustomLoginView

urlpatterns = [
    # لوحة الإدارة
    path('admin/', admin.site.urls),
    
    # نظام المصادقة
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # التطبيق الرئيسي
    path('', include('inventory.urls')),
]

# إضافة الملفات الثابتة في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

