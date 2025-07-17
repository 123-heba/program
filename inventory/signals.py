from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SaleInvoice, PurchaseInvoice, Revenue, Expense, RevenueCategory, ExpenseCategory


@receiver(post_save, sender=SaleInvoice)
def create_revenue_from_sale_invoice(sender, instance, created, **kwargs):
    """إنشاء إيراد تلقائياً عند إنشاء فاتورة مبيعات"""
    if created:
        # البحث عن فئة المبيعات أو إنشاؤها
        sales_category, _ = RevenueCategory.objects.get_or_create(
            name="مبيعات",
            defaults={
                'description': "إيرادات من المبيعات",
                'is_active': True
            }
        )
        
        # إنشاء سجل الإيراد
        Revenue.objects.create(
            title=f"مبيعات - فاتورة #{instance.invoice_number}",
            description=f"إيراد من فاتورة مبيعات للعميل: {instance.customer.name}",
            category=sales_category,
            revenue_type='sale',
            amount=instance.total_amount,
            payment_method='cash',  # يمكن تخصيصه لاحقاً
            date=instance.date,
            sale_invoice=instance,
            customer_name=instance.customer.name,
            created_by=instance.created_by
        )


@receiver(post_save, sender=PurchaseInvoice)
def create_expense_from_purchase_invoice(sender, instance, created, **kwargs):
    """إنشاء مصروف تلقائياً عند إنشاء فاتورة مشتريات"""
    if created:
        # البحث عن فئة المشتريات أو إنشاؤها
        purchase_category, _ = ExpenseCategory.objects.get_or_create(
            name="مشتريات",
            defaults={
                'description': "مصروفات المشتريات",
                'is_active': True
            }
        )
        
        # إنشاء سجل المصروف
        Expense.objects.create(
            title=f"مشتريات - فاتورة #{instance.invoice_number}",
            description=f"مصروف فاتورة مشتريات من المورد: {instance.supplier.name}",
            category=purchase_category,
            expense_type='purchase',
            amount=instance.total_amount,
            payment_method='cash',  # يمكن تخصيصه لاحقاً
            date=instance.date,
            purchase_invoice=instance,
            supplier_name=instance.supplier.name,
            created_by=instance.created_by
        )


@receiver(post_delete, sender=SaleInvoice)
def delete_revenue_on_sale_invoice_delete(sender, instance, **kwargs):
    """حذف الإيراد عند حذف فاتورة المبيعات"""
    try:
        if hasattr(instance, 'revenue_record') and instance.revenue_record:
            instance.revenue_record.delete()
    except Revenue.DoesNotExist:
        pass


@receiver(post_delete, sender=PurchaseInvoice)
def delete_expense_on_purchase_invoice_delete(sender, instance, **kwargs):
    """حذف المصروف عند حذف فاتورة المشتريات"""
    try:
        if hasattr(instance, 'expense_record') and instance.expense_record:
            instance.expense_record.delete()
    except Expense.DoesNotExist:
        pass


# إشارات تحديث المبالغ عند تعديل الفواتير
@receiver(post_save, sender=SaleInvoice)
def update_revenue_amount(sender, instance, created, **kwargs):
    """تحديث مبلغ الإيراد عند تعديل فاتورة المبيعات"""
    if not created and hasattr(instance, 'revenue_record') and instance.revenue_record:
        revenue = instance.revenue_record
        revenue.amount = instance.total_amount
        revenue.customer_name = instance.customer.name
        revenue.save()


@receiver(post_save, sender=PurchaseInvoice)
def update_expense_amount(sender, instance, created, **kwargs):
    """تحديث مبلغ المصروف عند تعديل فاتورة المشتريات"""
    if not created and hasattr(instance, 'expense_record') and instance.expense_record:
        expense = instance.expense_record
        expense.amount = instance.total_amount
        expense.supplier_name = instance.supplier.name
        expense.save()
