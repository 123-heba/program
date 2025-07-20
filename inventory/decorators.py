from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from .models import Employee


def employee_required(view_func):
    """
    ديكوريتر للتأكد من أن المستخدم موظف نشط
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        try:
            employee = request.user.employee_profile
            if not employee.is_active_employee:
                messages.error(request, "حسابك غير نشط. يرجى التواصل مع الإدارة.")
                return redirect('dashboard')
        except Employee.DoesNotExist:
            messages.error(request, "ليس لديك ملف موظف. يرجى التواصل مع الإدارة.")
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def permission_required(permission_codename, raise_exception=False):
    """
    ديكوريتر للتحقق من صلاحية معينة

    Args:
        permission_codename: رمز الصلاحية المطلوبة
        raise_exception: رفع استثناء بدلاً من إعادة توجيه
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # السماح للمدير العام بكل شيء
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                employee = request.user.employee_profile
                if not employee.is_active_employee:
                    if raise_exception:
                        raise PermissionDenied("حسابك غير نشط")
                    messages.error(request, "حسابك غير نشط. يرجى التواصل مع الإدارة.")
                    return redirect('dashboard')

                if not employee.has_permission(permission_codename):
                    if raise_exception:
                        raise PermissionDenied(f"ليس لديك صلاحية: {permission_codename}")
                    messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
                    return redirect('dashboard')

            except Employee.DoesNotExist:
                if raise_exception:
                    raise PermissionDenied("ليس لديك ملف موظف")
                messages.error(request, "ليس لديك ملف موظف. يرجى التواصل مع الإدارة.")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def role_required(role_name):
    """
    ديكوريتر للتحقق من دور وظيفي معين

    Args:
        role_name: اسم الدور المطلوب
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            # السماح للمدير العام بكل شيء
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            try:
                employee = request.user.employee_profile
                if not employee.is_active_employee:
                    messages.error(request, "حسابك غير نشط. يرجى التواصل مع الإدارة.")
                    return redirect('dashboard')

                if not employee.role or employee.role.name != role_name:
                    messages.error(request, f"يجب أن تكون {role_name} للوصول إلى هذه الصفحة.")
                    return redirect('dashboard')

            except Employee.DoesNotExist:
                messages.error(request, "ليس لديك ملف موظف. يرجى التواصل مع الإدارة.")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def manager_required(view_func):
    """
    ديكوريتر للتأكد من أن المستخدم مدير
    """
    return role_required("مدير")(view_func)


def admin_required(view_func):
    """
    ديكوريتر للتأكد من أن المستخدم مدير عام أو مدير نظام
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # السماح للمدير العام بكل شيء
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        try:
            employee = request.user.employee_profile
            if not employee.is_active_employee:
                messages.error(request, "حسابك غير نشط. يرجى التواصل مع الإدارة.")
                return redirect('dashboard')

            # التحقق من كون المستخدم مدير عام أو مدير نظام
            if (employee.role and
                employee.role.name in ["مدير عام", "مدير نظام"]):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "يجب أن تكون مدير عام أو مدير نظام للوصول إلى هذه الصفحة.")
                return redirect('dashboard')

        except Employee.DoesNotExist:
            messages.error(request, "ليس لديك ملف موظف. يرجى التواصل مع الإدارة.")
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


def superuser_required(view_func):
    """
    ديكوريتر للتأكد من أن المستخدم مدير عام فقط
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # السماح للمدير العام فقط
        if not request.user.is_superuser:
            messages.error(request, "هذه الصفحة متاحة للمدير العام فقط.")
            return redirect('dashboard')

        return view_func(request, *args, **kwargs)
    return _wrapped_view


# قائمة الصلاحيات المتاحة في النظام
SYSTEM_PERMISSIONS = {
    # صلاحيات المنتجات
    'view_products': 'عرض المنتجات',
    'add_products': 'إضافة المنتجات',
    'edit_products': 'تعديل المنتجات',
    'delete_products': 'حذف المنتجات',

    # صلاحيات الموردين
    'view_suppliers': 'عرض الموردين',
    'add_suppliers': 'إضافة الموردين',
    'edit_suppliers': 'تعديل الموردين',
    'delete_suppliers': 'حذف الموردين',

    # صلاحيات العملاء
    'view_customers': 'عرض العملاء',
    'add_customers': 'إضافة العملاء',
    'edit_customers': 'تعديل العملاء',
    'delete_customers': 'حذف العملاء',

    # صلاحيات فواتير الشراء
    'view_purchase_invoices': 'عرض فواتير الشراء',
    'add_purchase_invoices': 'إضافة فواتير الشراء',
    'edit_purchase_invoices': 'تعديل فواتير الشراء',
    'delete_purchase_invoices': 'حذف فواتير الشراء',

    # صلاحيات فواتير البيع
    'view_sale_invoices': 'عرض فواتير البيع',
    'add_sale_invoices': 'إضافة فواتير البيع',
    'edit_sale_invoices': 'تعديل فواتير البيع',
    'delete_sale_invoices': 'حذف فواتير البيع',

    # صلاحيات الطلبات
    'view_orders': 'عرض الطلبات',
    'add_orders': 'إضافة الطلبات',
    'edit_orders': 'تعديل الطلبات',
    'delete_orders': 'حذف الطلبات',
    'process_orders': 'معالجة الطلبات',

    # صلاحيات إدارة الفريق
    'view_employees': 'عرض الموظفين',
    'add_employees': 'إضافة الموظفين',
    'edit_employees': 'تعديل الموظفين',
    'delete_employees': 'حذف الموظفين',
    'manage_roles': 'إدارة الأدوار',
    'manage_permissions': 'إدارة الصلاحيات',

    # صلاحيات التقارير
    'view_reports': 'عرض التقارير',
    'export_data': 'تصدير البيانات',

    # صلاحيات النظام
    'system_settings': 'إعدادات النظام',
    'backup_restore': 'النسخ الاحتياطي والاستعادة',
}
