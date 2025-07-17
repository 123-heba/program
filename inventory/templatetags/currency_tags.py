from django import template
from decimal import Decimal
from ..currency_settings import format_currency, get_currency_symbol, get_currency_name

register = template.Library()

@register.filter
def currency(value, show_symbol=True):
    """
    تنسيق المبلغ بالعملة المصرية
    
    Usage:
        {{ amount|currency }}
        {{ amount|currency:False }}  # بدون رمز العملة
    """
    return format_currency(value, show_symbol)

@register.filter
def currency_no_symbol(value):
    """
    تنسيق المبلغ بدون رمز العملة
    
    Usage:
        {{ amount|currency_no_symbol }}
    """
    return format_currency(value, show_symbol=False)

@register.simple_tag
def currency_symbol():
    """
    الحصول على رمز العملة
    
    Usage:
        {% currency_symbol %}
    """
    return get_currency_symbol()

@register.simple_tag
def currency_name():
    """
    الحصول على اسم العملة
    
    Usage:
        {% currency_name %}
    """
    return get_currency_name()

@register.filter
def multiply(value, arg):
    """
    ضرب قيمتين
    
    Usage:
        {{ price|multiply:quantity }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """
    حساب النسبة المئوية
    
    Usage:
        {{ part|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0
