# إعدادات العملة للنظام

# العملة الأساسية
CURRENCY_CODE = "EGP"
CURRENCY_NAME = "جنيه مصري"
CURRENCY_SYMBOL = "ج.م"
CURRENCY_SYMBOL_SHORT = "ج.م"

# إعدادات التنسيق
CURRENCY_DECIMAL_PLACES = 2
CURRENCY_THOUSAND_SEPARATOR = ","
CURRENCY_DECIMAL_SEPARATOR = "."

# دالة لتنسيق العملة
def format_currency(amount, show_symbol=True, decimal_places=None):
    """
    تنسيق المبلغ بالعملة المصرية
    
    Args:
        amount: المبلغ المراد تنسيقه
        show_symbol: إظهار رمز العملة أم لا
        decimal_places: عدد الخانات العشرية (افتراضي: 2)
    
    Returns:
        str: المبلغ منسق بالعملة
    """
    if amount is None:
        amount = 0
    
    if decimal_places is None:
        decimal_places = CURRENCY_DECIMAL_PLACES
    
    # تحويل إلى float إذا كان Decimal
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        amount = 0
    
    # تنسيق الرقم
    formatted_amount = f"{amount:,.{decimal_places}f}"
    
    # إضافة رمز العملة
    if show_symbol:
        return f"{formatted_amount} {CURRENCY_SYMBOL}"
    else:
        return formatted_amount

# دالة للحصول على رمز العملة
def get_currency_symbol():
    """الحصول على رمز العملة"""
    return CURRENCY_SYMBOL

# دالة للحصول على اسم العملة
def get_currency_name():
    """الحصول على اسم العملة"""
    return CURRENCY_NAME

# دالة للحصول على كود العملة
def get_currency_code():
    """الحصول على كود العملة"""
    return CURRENCY_CODE
