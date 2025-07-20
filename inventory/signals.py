from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SaleInvoice, PurchaseInvoice, Revenue, Expense, RevenueCategory, ExpenseCategory, Product, Order
from .tasks import update_woocommerce_stock, create_shipment_for_order
import logging

logger = logging.getLogger(__name__)


# تعطيل جميع الـ signals مؤقت<|im_start|> لتجنب مشاكل Celery

# @receiver(post_save, sender=PurchaseInvoice)
# def create_expense_from_purchase_invoice(sender, instance, created, **kwargs):
#     """إنشاء مصروف تلقائي عند إنشاء فاتورة مشتريات"""
#     pass

# @receiver(post_delete, sender=SaleInvoice)
# def delete_revenue_on_sale_invoice_delete(sender, instance, **kwargs):
#     """حذف الإيراد عند حذف فاتورة المبيعات"""
#     pass

# @receiver(post_delete, sender=PurchaseInvoice)
# def delete_expense_on_purchase_invoice_delete(sender, instance, **kwargs):
#     """حذف المصروف عند حذف فاتورة المشتريات"""
#     pass

# @receiver(post_save, sender=SaleInvoice)
# def update_revenue_amount(sender, instance, created, **kwargs):
#     """تحديث مبلغ الإيراد عند تعديل فاتورة المبيعات"""
#     pass

# @receiver(post_save, sender=PurchaseInvoice)
# def update_expense_amount(sender, instance, created, **kwargs):
#     """تحديث مبلغ المصروف عند تعديل فاتورة المشتريات"""
#     pass

# @receiver(post_save, sender=Product)
# def sync_product_stock_to_woocommerce(sender, instance, **kwargs):
#     """تحديث المخزون في WooCommerce عند تغيير الكمية"""
#     pass

# @receiver(post_save, sender=Order)
# def auto_create_shipment(sender, instance, created, **kwargs):
#     """إنشاء شحنة تلقائية عند تأكيد الطلب"""
#     pass

pass
