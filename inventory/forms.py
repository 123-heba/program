from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Product, Supplier, Customer, PurchaseInvoice, SaleInvoice,
    Order, OrderItem, Employee, Role, Permission,
    SaleReturn, SaleReturnItem, PurchaseReturn, PurchaseReturnItem,
    Revenue, Expense, RevenueCategory, ExpenseCategory
)
from .decorators import SYSTEM_PERMISSIONS


class SupplierForm(forms.ModelForm):
    """نموذج إضافة وتعديل الموردين"""

    class Meta:
        model = Supplier
        fields = ["name", "phone", "email", "address"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "اسم المورد"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "رقم الهاتف"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "البريد الإلكتروني (اختياري)"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "العنوان (اختياري)"
            }),
        }
        labels = {
            "name": "اسم المورد",
            "phone": "رقم الهاتف",
            "email": "البريد الإلكتروني",
            "address": "العنوان",
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and len(phone) < 10:
            raise ValidationError("رقم الهاتف يجب أن يكون 10 أرقام على الأقل")
        return phone


class CustomerForm(forms.ModelForm):
    """نموذج إضافة وتعديل العملاء"""

    class Meta:
        model = Customer
        fields = ["name", "phone", "email", "address"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "اسم العميل"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "رقم الهاتف"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "البريد الإلكتروني (اختياري)"
            }),
            "address": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "العنوان (اختياري)"
            }),
        }
        labels = {
            "name": "اسم العميل",
            "phone": "رقم الهاتف",
            "email": "البريد الإلكتروني",
            "address": "العنوان",
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and len(phone) < 10:
            raise ValidationError("رقم الهاتف يجب أن يكون 10 أرقام على الأقل")
        return phone


class ProductForm(forms.ModelForm):
    """نموذج إضافة وتعديل المنتجات"""

    class Meta:
        model = Product
        fields = ["name", "description", "price", "quantity", "min_quantity", "supplier"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "اسم المنتج"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "وصف المنتج (اختياري)"
            }),
            "price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "0.00"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "0"
            }),
            "min_quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "5"
            }),
            "supplier": forms.Select(attrs={
                "class": "form-select"
            }),
        }
        labels = {
            "name": "اسم المنتج",
            "description": "الوصف",
            "price": "السعر (ر.س)",
            "quantity": "الكمية في المخزن",
            "min_quantity": "الحد الأدنى للكمية",
            "supplier": "المورد",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Supplier.objects.all()
        self.fields["supplier"].empty_label = "اختر المورد"

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price and price <= 0:
            raise ValidationError("السعر يجب أن يكون أكبر من صفر")
        return price

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity and quantity < 0:
            raise ValidationError("الكمية لا يمكن أن تكون سالبة")
        return quantity

    def clean_min_quantity(self):
        min_quantity = self.cleaned_data.get("min_quantity")
        if min_quantity and min_quantity < 0:
            raise ValidationError("الحد الأدنى للكمية لا يمكن أن يكون سالباً")
        return min_quantity


class PurchaseInvoiceForm(forms.ModelForm):
    """نموذج إنشاء فاتورة شراء"""

    class Meta:
        model = PurchaseInvoice
        fields = ["supplier", "notes"]
        widgets = {
            "supplier": forms.Select(attrs={
                "class": "form-select"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "ملاحظات (اختياري)"
            }),
        }
        labels = {
            "supplier": "المورد",
            "notes": "ملاحظات",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["supplier"].queryset = Supplier.objects.all()
        self.fields["supplier"].empty_label = "اختر المورد"


class SaleInvoiceForm(forms.ModelForm):
    """نموذج إنشاء فاتورة بيع"""

    class Meta:
        model = SaleInvoice
        fields = ["customer", "notes"]
        widgets = {
            "customer": forms.Select(attrs={
                "class": "form-select"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "ملاحظات (اختياري)"
            }),
        }
        labels = {
            "customer": "العميل",
            "notes": "ملاحظات",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.all()
        self.fields["customer"].empty_label = "اختر العميل"


class ProductSearchForm(forms.Form):
    """نموذج البحث عن المنتجات"""
    search = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "ابحث عن منتج..."
        }),
        label="البحث"
    )

    supplier = forms.ModelChoiceField(
        queryset=Supplier.objects.all(),
        required=False,
        empty_label="جميع الموردين",
        widget=forms.Select(attrs={
            "class": "form-select"
        }),
        label="المورد"
    )

    STOCK_CHOICES = [
        ("", "جميع المنتجات"),
        ("low", "مخزون منخفض"),
        ("out", "نفد المخزون"),
    ]

    stock_status = forms.ChoiceField(
        choices=STOCK_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            "class": "form-select"
        }),
        label="حالة المخزون"
    )


class DateRangeForm(forms.Form):
    """نموذج اختيار فترة زمنية للتقارير"""
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        }),
        label="من تاريخ"
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            "class": "form-control",
            "type": "date"
        }),
        label="إلى تاريخ"
    )

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("تاريخ البداية يجب أن يكون قبل تاريخ النهاية")

        return cleaned_data


class OrderForm(forms.ModelForm):
    """نموذج إضافة وتعديل الطلبات"""

    class Meta:
        model = Order
        fields = ["customer", "notes", "status"]
        widgets = {
            "customer": forms.Select(attrs={
                "class": "form-select"
            }),
            "notes": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "ملاحظات (اختياري)"
            }),
            "status": forms.Select(attrs={
                "class": "form-select"
            }),
        }
        labels = {
            "customer": "العميل",
            "notes": "ملاحظات",
            "status": "الحالة",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["customer"].queryset = Customer.objects.all()
        self.fields["customer"].empty_label = "اختر العميل"


class OrderItemForm(forms.ModelForm):
    """نموذج إضافة وتعديل عناصر الطلب"""

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "unit_price"]
        widgets = {
            "product": forms.Select(attrs={
                "class": "form-select"
            }),
            "quantity": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "الكمية"
            }),
            "unit_price": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0.01",
                "placeholder": "سعر الوحدة"
            }),
        }
        labels = {
            "product": "المنتج",
            "quantity": "الكمية",
            "unit_price": "سعر الوحدة",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.all()
        self.fields["product"].empty_label = "اختر المنتج"

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get("product")
        quantity = cleaned_data.get("quantity")

        if product and quantity:
            if quantity > product.quantity:
                raise ValidationError(
                    f"الكمية المطلوبة من {product.name} ({quantity}) أكبر من الكمية المتوفرة في المخزن ({product.quantity}).")
        return cleaned_data


# نماذج إدارة الموظفين والأدوار

class EmployeeUserForm(UserCreationForm):
    """نموذج إنشاء حساب مستخدم للموظف"""
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الاسم الأول'
        }),
        label="الاسم الأول"
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'الاسم الأخير'
        }),
        label="الاسم الأخير"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'البريد الإلكتروني'
        }),
        label="البريد الإلكتروني"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المستخدم'
            }),
        }
        labels = {
            'username': 'اسم المستخدم',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = "كلمة المرور"
        self.fields['password2'].label = "تأكيد كلمة المرور"


class EmployeeForm(forms.ModelForm):
    """نموذج إضافة وتعديل بيانات الموظف"""

    class Meta:
        model = Employee
        fields = [
            'role', 'department', 'phone', 'address',
            'hire_date', 'salary', 'employment_status', 'notes'
        ]
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'القسم'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'العنوان'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': 0.01
            }),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات'
            }),
        }
        labels = {
            'role': 'الدور الوظيفي',
            'department': 'القسم',
            'phone': 'رقم الهاتف',
            'address': 'العنوان',
            'hire_date': 'تاريخ التوظيف',
            'salary': 'الراتب',
            'employment_status': 'حالة التوظيف',
            'notes': 'ملاحظات',
        }


class RoleForm(forms.ModelForm):
    """نموذج إضافة وتعديل الأدوار الوظيفية"""

    class Meta:
        model = Role
        fields = ['name', 'description', 'permissions', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الدور الوظيفي'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الدور الوظيفي'
            }),
            'permissions': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': 10
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'اسم الدور',
            'description': 'الوصف',
            'permissions': 'الصلاحيات',
            'is_active': 'نشط',
        }


class PermissionForm(forms.ModelForm):
    """نموذج إضافة وتعديل الصلاحيات"""

    class Meta:
        model = Permission
        fields = ['name', 'codename', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الصلاحية'
            }),
            'codename': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رمز الصلاحية'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الصلاحية'
            }),
        }
        labels = {
            'name': 'اسم الصلاحية',
            'codename': 'الرمز',
            'description': 'الوصف',
        }


# ========== نماذج المرتجعات ==========

class SaleReturnForm(forms.ModelForm):
    """نموذج إنشاء مرتجع مبيعات"""

    class Meta:
        model = SaleReturn
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اذكر سبب إرجاع البضاعة...'
            }),
        }
        labels = {
            'reason': 'سبب المرتجع',
        }


class SaleReturnItemForm(forms.Form):
    """نموذج عنصر مرتجع مبيعات"""
    returned_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control returned-quantity',
            'min': '1',
            'placeholder': '0'
        }),
        label='الكمية المرتجعة'
    )

    def __init__(self, *args, **kwargs):
        self.original_item = kwargs.pop('original_item', None)
        super().__init__(*args, **kwargs)

        if self.original_item:
            # تحديد الحد الأقصى للكمية المرتجعة
            self.fields['returned_quantity'].widget.attrs['max'] = self.original_item.quantity
            self.fields['returned_quantity'].help_text = f'الحد الأقصى: {self.original_item.quantity}'

    def clean_returned_quantity(self):
        returned_quantity = self.cleaned_data.get('returned_quantity')

        if self.original_item and returned_quantity:
            if returned_quantity > self.original_item.quantity:
                raise ValidationError(
                    f'الكمية المرتجعة ({returned_quantity}) لا يمكن أن تكون أكبر من الكمية الأصلية ({self.original_item.quantity})'
                )

        return returned_quantity


class PurchaseReturnForm(forms.ModelForm):
    """نموذج إنشاء مرتجع مشتريات"""

    class Meta:
        model = PurchaseReturn
        fields = ['reason']
        widgets = {
            'reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'اذكر سبب إرجاع البضاعة للمورد...'
            }),
        }
        labels = {
            'reason': 'سبب المرتجع',
        }


class PurchaseReturnItemForm(forms.Form):
    """نموذج عنصر مرتجع مشتريات"""
    returned_quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control returned-quantity',
            'min': '1',
            'placeholder': '0'
        }),
        label='الكمية المرتجعة'
    )

    def __init__(self, *args, **kwargs):
        self.original_item = kwargs.pop('original_item', None)
        super().__init__(*args, **kwargs)

        if self.original_item:
            # تحديد الحد الأقصى للكمية المرتجعة
            self.fields['returned_quantity'].widget.attrs['max'] = self.original_item.quantity
            self.fields['returned_quantity'].help_text = f'الحد الأقصى: {self.original_item.quantity}'

    def clean_returned_quantity(self):
        returned_quantity = self.cleaned_data.get('returned_quantity')

        if self.original_item and returned_quantity:
            if returned_quantity > self.original_item.quantity:
                raise ValidationError(
                    f'الكمية المرتجعة ({returned_quantity}) لا يمكن أن تكون أكبر من الكمية الأصلية ({self.original_item.quantity})'
                )

            # التحقق من توفر الكمية في المخزون للمرتجع
            if returned_quantity > self.original_item.product.quantity:
                raise ValidationError(
                    f'الكمية المرتجعة ({returned_quantity}) أكبر من الكمية المتوفرة في المخزون ({self.original_item.product.quantity})'
                )

        return returned_quantity


# ========== نماذج الإيرادات والمصروفات ==========

class RevenueCategoryForm(forms.ModelForm):
    """نموذج فئات الإيرادات"""

    class Meta:
        model = RevenueCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم فئة الإيراد'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الفئة (اختياري)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ExpenseCategoryForm(forms.ModelForm):
    """نموذج فئات المصروفات"""

    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم فئة المصروف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الفئة (اختياري)'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class RevenueForm(forms.ModelForm):
    """نموذج الإيرادات"""

    class Meta:
        model = Revenue
        fields = [
            'title', 'description', 'category', 'revenue_type',
            'amount', 'payment_method', 'date', 'customer_name', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الإيراد'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف الإيراد'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'revenue_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم العميل (اختياري)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = RevenueCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = "اختر فئة الإيراد"


class ExpenseForm(forms.ModelForm):
    """نموذج المصروفات"""

    class Meta:
        model = Expense
        fields = [
            'title', 'description', 'category', 'expense_type',
            'amount', 'payment_method', 'date', 'supplier_name',
            'receipt_number', 'notes'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان المصروف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المصروف'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expense_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0.00'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-select'
            }),
            'date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المورد (اختياري)'
            }),
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الإيصال (اختياري)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'ملاحظات إضافية'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ExpenseCategory.objects.filter(is_active=True)
        self.fields['category'].empty_label = "اختر فئة المصروف"

