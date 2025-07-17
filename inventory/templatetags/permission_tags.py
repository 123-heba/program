from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.filter
def is_manager(user):
    """التحقق من كون المستخدم مدير"""
    if not user.is_authenticated:
        return False
    
    # المدير العام له صلاحيات كاملة
    if user.is_superuser:
        return True
    
    try:
        employee = user.employee_profile
        return employee.is_manager
    except:
        return False


@register.filter
def can_manage_employees(user):
    """التحقق من إمكانية إدارة الموظفين"""
    if not user.is_authenticated:
        return False
    
    # المدير العام له صلاحيات كاملة
    if user.is_superuser:
        return True
    
    try:
        employee = user.employee_profile
        return employee.can_manage_employees
    except:
        return False


@register.filter
def can_manage_roles(user):
    """التحقق من إمكانية إدارة الأدوار"""
    if not user.is_authenticated:
        return False
    
    # المدير العام له صلاحيات كاملة
    if user.is_superuser:
        return True
    
    try:
        employee = user.employee_profile
        return employee.can_manage_roles
    except:
        return False


@register.filter
def has_permission(user, permission_codename):
    """التحقق من وجود صلاحية معينة"""
    if not user.is_authenticated:
        return False
    
    # المدير العام له صلاحيات كاملة
    if user.is_superuser:
        return True
    
    try:
        employee = user.employee_profile
        return employee.has_permission(permission_codename)
    except:
        return False


@register.filter
def get_user_role(user):
    """الحصول على دور المستخدم"""
    if not user.is_authenticated:
        return "غير مسجل"
    
    if user.is_superuser:
        return "مدير عام"
    
    try:
        employee = user.employee_profile
        if employee.role:
            return employee.role.name
        else:
            return "موظف"
    except:
        return "مستخدم"


@register.simple_tag
def user_display_name(user):
    """عرض اسم المستخدم مع دوره"""
    if not user.is_authenticated:
        return "غير مسجل"
    
    name = user.get_full_name() or user.username
    role = get_user_role(user)
    
    return f"{name} ({role})"
