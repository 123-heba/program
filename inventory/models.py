from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone


# نماذج إدارة فريق العمل والصلاحيات
class Permission(models.Model):
    """نموذج الصلاحيات"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الصلاحية")
    codename = models.CharField(max_length=100, unique=True, verbose_name="الرمز")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "صلاحية"
        verbose_name_plural = "الصلاحيات"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Role(models.Model):
    """نموذج الأدوار الوظيفية"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم الدور")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name="الصلاحيات",
        related_name="roles"
    )
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "دور وظيفي"
        verbose_name_plural = "الأدوار الوظيفية"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def has_permission(self, permission_codename):
        """التحقق من وجود صلاحية معينة"""
        return self.permissions.filter(codename=permission_codename).exists()


class Employee(models.Model):
    """نموذج الموظفين"""
    EMPLOYMENT_STATUS_CHOICES = [
        ("active", "نشط"),
        ("inactive", "غير نشط"),
        ("suspended", "موقوف"),
        ("terminated", "منتهي الخدمة"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name="المستخدم",
        related_name="employee_profile"
    )
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم الموظف"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الدور الوظيفي"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="القسم"
    )
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    hire_date = models.DateField(verbose_name="تاريخ التوظيف")
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="الراتب"
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default="active",
        verbose_name="حالة التوظيف"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "موظف"
        verbose_name_plural = "الموظفين"
        ordering = ["employee_id"]

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name() or self.user.username}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            # إنشاء رقم موظف تلقائي
            last_employee = Employee.objects.order_by("-id").first()
            if last_employee:
                last_number = int(last_employee.employee_id.split("-")[-1])
                self.employee_id = f"EMP-{last_number + 1:04d}"
            else:
                self.employee_id = "EMP-0001"
        super().save(*args, **kwargs)

    def has_permission(self, permission_codename):
        """التحقق من وجود صلاحية معينة للموظف"""
        if self.role:
            return self.role.has_permission(permission_codename)
        return False

    @property
    def is_active_employee(self):
        """التحقق من كون الموظف نشط"""
        return self.employment_status == "active"

    @property
    def full_name(self):
        """الحصول على الاسم الكامل"""
        return self.user.get_full_name() or self.user.username

    @property
    def service_duration(self):
        """حساب مدة الخدمة"""
        from datetime import date
        if self.hire_date:
            today = date.today()
            delta = today - self.hire_date
            years = delta.days // 365
            months = (delta.days % 365) // 30

            if years > 0:
                if months > 0:
                    return f"{years} سنة و {months} شهر"
                else:
                    return f"{years} سنة"
            elif months > 0:
                return f"{months} شهر"
            else:
                return "أقل من شهر"
        return "غير محدد"

    @property
    def is_manager(self):
        """التحقق من كون الموظف مدير"""
        if not self.role:
            return False

        # أسماء الأدوار التي تعتبر إدارية
        manager_roles = [
            "مدير عام", "مدير نظام", "مدير", "مدير مبيعات",
            "مدير مخزون", "مدير مالي", "مدير تقني"
        ]

        return (
            self.role.name in manager_roles or
            self.role.has_permission('manage_employees') or
            self.role.has_permission('manage_roles')
        )

    @property
    def can_manage_employees(self):
        """التحقق من إمكانية إدارة الموظفين"""
        return (
            self.is_manager or
            (self.role and self.role.has_permission('manage_employees'))
        )

    @property
    def can_manage_roles(self):
        """التحقق من إمكانية إدارة الأدوار"""
        return (
            self.is_manager or
            (self.role and self.role.has_permission('manage_roles'))
        )

    def has_permission(self, permission_codename):
        """التحقق من وجود صلاحية معينة للموظف"""
        if not self.role:
            return False
        return self.role.has_permission(permission_codename)


class Supplier(models.Model):
    """نموذج الموردين"""
    name = models.CharField(max_length=200, verbose_name="اسم المورد")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مورد"
        verbose_name_plural = "الموردين"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Customer(models.Model):
    """نموذج العملاء"""
    name = models.CharField(max_length=200, verbose_name="اسم العميل")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    email = models.EmailField(blank=True, null=True, verbose_name="البريد الإلكتروني")
    address = models.TextField(blank=True, null=True, verbose_name="العنوان")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """نموذج المنتجات"""
    name = models.CharField(max_length=200, verbose_name="اسم المنتج")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="السعر",
    )
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="الكمية في المخزن",
    )
    min_quantity = models.IntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        verbose_name="الحد الأدنى للكمية",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        verbose_name="المورد",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        """التحقق من انخفاض المخزون"""
        return self.quantity <= self.min_quantity

    @property
    def total_value(self):
        """القيمة الإجمالية للمنتج في المخزن"""
        return self.price * self.quantity

    @property
    def barcode_data(self):
        """إنشاء بيانات الباركود من ID المنتج"""
        # تحويل ID إلى باركود بتنسيق Code 128
        return f"PRD{self.id:06d}"  # مثال: PRD000001

    @property
    def barcode_display(self):
        """عرض الباركود كنص مقروء"""
        return self.barcode_data


class PurchaseInvoice(models.Model):
    """نموذج فواتير الشراء"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        verbose_name="المورد",
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفاتورة")
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="المبلغ الإجمالي",
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="أنشئت بواسطة",
    )

    class Meta:
        verbose_name = "فاتورة شراء"
        verbose_name_plural = "فواتير الشراء"
        ordering = ["-date"]

    def __str__(self):
        return f"فاتورة شراء رقم {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # إنشاء رقم فاتورة تلقائي
            last_invoice = PurchaseInvoice.objects.order_by("-id").first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split("-")[-1])
                self.invoice_number = f"PUR-{last_number + 1:06d}"
            else:
                self.invoice_number = "PUR-000001"
        super().save(*args, **kwargs)


class PurchaseInvoiceItem(models.Model):
    """نموذج عناصر فاتورة الشراء"""
    invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="الفاتورة",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="المنتج",
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="الكمية",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="سعر الوحدة",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="السعر الإجمالي",
    )

    class Meta:
        verbose_name = "عنصر فاتورة شراء"
        verbose_name_plural = "عناصر فواتير الشراء"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class SaleInvoice(models.Model):
    """نموذج فواتير البيع"""
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الفاتورة")
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name="العميل",
    )
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الفاتورة")
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="المبلغ الإجمالي",
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="أنشئت بواسطة",
    )

    class Meta:
        verbose_name = "فاتورة بيع"
        verbose_name_plural = "فواتير البيع"
        ordering = ["-date"]

    def __str__(self):
        return f"فاتورة بيع رقم {self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # إنشاء رقم فاتورة تلقائي
            last_invoice = SaleInvoice.objects.order_by("-id").first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split("-")[-1])
                self.invoice_number = f"SAL-{last_number + 1:06d}"
            else:
                self.invoice_number = "SAL-000001"
        super().save(*args, **kwargs)


class SaleInvoiceItem(models.Model):
    """نموذج عناصر فاتورة البيع"""
    invoice = models.ForeignKey(
        SaleInvoice,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="الفاتورة",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="المنتج",
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="الكمية",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="سعر الوحدة",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="السعر الإجمالي",
    )

    class Meta:
        verbose_name = "عنصر فاتورة بيع"
        verbose_name_plural = "عناصر فواتير البيع"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


class Order(models.Model):
    """نموذج الطلبات"""
    STATUS_CHOICES = [
        ("pending", "قيد المعالجة"),
        ("processing", "جاري التجهيز"),
        ("shipped", "تم الشحن"),
        ("delivered", "تم التسليم"),
        ("cancelled", "ملغى"),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name="العميل",
    )
    order_number = models.CharField(max_length=50, unique=True, verbose_name="رقم الطلب")
    order_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="الحالة",
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="المبلغ الإجمالي",
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="أنشئ بواسطة",
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ["-order_date"]

    def __str__(self):
        return f"طلب رقم {self.order_number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by("-id").first()
            if last_order:
                last_number = int(last_order.order_number.split("-")[-1])
                self.order_number = f"ORD-{last_number + 1:06d}"
            else:
                self.order_number = "ORD-000001"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """نموذج عناصر الطلب"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="الطلب",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="المنتج",
    )
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="الكمية",
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="سعر الوحدة",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="السعر الإجمالي",
    )

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلبات"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"


# ========== نماذج المرتجعات ==========

class SaleReturn(models.Model):
    """مرتجع فاتورة مبيعات"""
    original_invoice = models.ForeignKey(
        SaleInvoice,
        on_delete=models.CASCADE,
        verbose_name="الفاتورة الأصلية",
        related_name="returns"
    )
    return_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم المرتجع"
    )
    return_date = models.DateField(
        auto_now_add=True,
        verbose_name="تاريخ المرتجع"
    )
    reason = models.TextField(
        verbose_name="سبب المرتجع",
        help_text="اذكر سبب إرجاع البضاعة"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="إجمالي قيمة المرتجع"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="تم الإنشاء بواسطة"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "مرتجع مبيعات"
        verbose_name_plural = "مرتجعات المبيعات"
        ordering = ['-return_date', '-id']

    def save(self, *args, **kwargs):
        if not self.return_number:
            # إنشاء رقم مرتجع تلقائي
            last_return = SaleReturn.objects.filter(
                return_number__startswith='SR'
            ).order_by('-id').first()

            if last_return:
                last_number = int(last_return.return_number[2:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.return_number = f"SR{new_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"مرتجع #{self.return_number} - فاتورة #{self.original_invoice.invoice_number}"


class SaleReturnItem(models.Model):
    """عنصر مرتجع مبيعات"""
    sale_return = models.ForeignKey(
        SaleReturn,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="مرتجع المبيعات"
    )
    original_item = models.ForeignKey(
        SaleInvoiceItem,
        on_delete=models.CASCADE,
        verbose_name="العنصر الأصلي"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="المنتج"
    )
    returned_quantity = models.PositiveIntegerField(
        verbose_name="الكمية المرتجعة"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="سعر الوحدة"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="إجمالي السعر"
    )

    class Meta:
        verbose_name = "عنصر مرتجع مبيعات"
        verbose_name_plural = "عناصر مرتجعات المبيعات"

    def save(self, *args, **kwargs):
        # حساب إجمالي السعر
        self.total_price = self.returned_quantity * self.unit_price
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - كمية: {self.returned_quantity}"


class PurchaseReturn(models.Model):
    """مرتجع فاتورة مشتريات"""
    original_invoice = models.ForeignKey(
        PurchaseInvoice,
        on_delete=models.CASCADE,
        verbose_name="الفاتورة الأصلية",
        related_name="returns"
    )
    return_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم المرتجع"
    )
    return_date = models.DateField(
        auto_now_add=True,
        verbose_name="تاريخ المرتجع"
    )
    reason = models.TextField(
        verbose_name="سبب المرتجع",
        help_text="اذكر سبب إرجاع البضاعة للمورد"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="إجمالي قيمة المرتجع"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="تم الإنشاء بواسطة"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاريخ الإنشاء"
    )

    class Meta:
        verbose_name = "مرتجع مشتريات"
        verbose_name_plural = "مرتجعات المشتريات"
        ordering = ['-return_date', '-id']

    def save(self, *args, **kwargs):
        if not self.return_number:
            # إنشاء رقم مرتجع تلقائي
            last_return = PurchaseReturn.objects.filter(
                return_number__startswith='PR'
            ).order_by('-id').first()

            if last_return:
                last_number = int(last_return.return_number[2:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.return_number = f"PR{new_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"مرتجع #{self.return_number} - فاتورة #{self.original_invoice.invoice_number}"


class PurchaseReturnItem(models.Model):
    """عنصر مرتجع مشتريات"""
    purchase_return = models.ForeignKey(
        PurchaseReturn,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="مرتجع المشتريات"
    )
    original_item = models.ForeignKey(
        PurchaseInvoiceItem,
        on_delete=models.CASCADE,
        verbose_name="العنصر الأصلي"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="المنتج"
    )
    returned_quantity = models.PositiveIntegerField(
        verbose_name="الكمية المرتجعة"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="سعر الوحدة"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="إجمالي السعر"
    )

    class Meta:
        verbose_name = "عنصر مرتجع مشتريات"
        verbose_name_plural = "عناصر مرتجعات المشتريات"

    def save(self, *args, **kwargs):
        # حساب إجمالي السعر
        self.total_price = self.returned_quantity * self.unit_price
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} - كمية: {self.returned_quantity}"


# ========== نماذج الإيرادات والمصروفات ==========

class RevenueCategory(models.Model):
    """فئات الإيرادات"""
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "فئة إيراد"
        verbose_name_plural = "فئات الإيرادات"
        ordering = ['name']

    def __str__(self):
        return self.name


class ExpenseCategory(models.Model):
    """فئات المصروفات"""
    name = models.CharField(max_length=100, verbose_name="اسم الفئة")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    is_active = models.BooleanField(default=True, verbose_name="نشط")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        verbose_name = "فئة مصروف"
        verbose_name_plural = "فئات المصروفات"
        ordering = ['name']

    def __str__(self):
        return self.name


class Revenue(models.Model):
    """نموذج الإيرادات"""
    REVENUE_TYPES = [
        ('sale', 'مبيعات'),
        ('service', 'خدمات'),
        ('other', 'أخرى'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'نقدي'),
        ('bank_transfer', 'تحويل بنكي'),
        ('credit_card', 'بطاقة ائتمان'),
        ('check', 'شيك'),
        ('other', 'أخرى'),
    ]

    reference_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم المرجع"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان الإيراد")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    category = models.ForeignKey(
        RevenueCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الفئة"
    )
    revenue_type = models.CharField(
        max_length=20,
        choices=REVENUE_TYPES,
        default='other',
        verbose_name="نوع الإيراد"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="المبلغ"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        verbose_name="طريقة الدفع"
    )
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")

    # ربط بفاتورة المبيعات (اختياري)
    sale_invoice = models.OneToOneField(
        'SaleInvoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='revenue_record',
        verbose_name="فاتورة المبيعات"
    )

    # معلومات إضافية
    customer_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="اسم العميل"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    # معلومات النظام
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="تم الإنشاء بواسطة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "إيراد"
        verbose_name_plural = "الإيرادات"
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # إنشاء رقم مرجع تلقائي
            last_revenue = Revenue.objects.filter(
                reference_number__startswith='REV'
            ).order_by('-id').first()

            if last_revenue:
                last_number = int(last_revenue.reference_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.reference_number = f"REV{new_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} - {self.title} - {self.amount} ر.س"


class Expense(models.Model):
    """نموذج المصروفات"""
    EXPENSE_TYPES = [
        ('purchase', 'مشتريات'),
        ('operational', 'تشغيلية'),
        ('administrative', 'إدارية'),
        ('marketing', 'تسويقية'),
        ('maintenance', 'صيانة'),
        ('other', 'أخرى'),
    ]

    PAYMENT_METHODS = [
        ('cash', 'نقدي'),
        ('bank_transfer', 'تحويل بنكي'),
        ('credit_card', 'بطاقة ائتمان'),
        ('check', 'شيك'),
        ('other', 'أخرى'),
    ]

    reference_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="رقم المرجع"
    )
    title = models.CharField(max_length=200, verbose_name="عنوان المصروف")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="الفئة"
    )
    expense_type = models.CharField(
        max_length=20,
        choices=EXPENSE_TYPES,
        default='other',
        verbose_name="نوع المصروف"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="المبلغ"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash',
        verbose_name="طريقة الدفع"
    )
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")

    # ربط بفاتورة المشتريات (اختياري)
    purchase_invoice = models.OneToOneField(
        'PurchaseInvoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='expense_record',
        verbose_name="فاتورة المشتريات"
    )

    # معلومات إضافية
    supplier_name = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="اسم المورد"
    )
    receipt_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="رقم الإيصال"
    )
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")

    # معلومات النظام
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="تم الإنشاء بواسطة"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مصروف"
        verbose_name_plural = "المصروفات"
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.reference_number:
            # إنشاء رقم مرجع تلقائي
            last_expense = Expense.objects.filter(
                reference_number__startswith='EXP'
            ).order_by('-id').first()

            if last_expense:
                last_number = int(last_expense.reference_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1

            self.reference_number = f"EXP{new_number:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.reference_number} - {self.title} - {self.amount} ر.س"



