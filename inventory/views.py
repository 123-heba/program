from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q, Sum, Count, F
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
import json
from decimal import Decimal
from .decorators import admin_required, permission_required
from .models import PurchaseInvoiceItem, Product
from .models import (
    Product, Supplier, Customer,
    PurchaseInvoice, PurchaseInvoiceItem,
    SaleInvoice, SaleInvoiceItem, Order, OrderItem,
    Employee, Role, Permission,
    SaleReturn, SaleReturnItem, PurchaseReturn, PurchaseReturnItem,
    Revenue, Expense, RevenueCategory, ExpenseCategory
)
from .forms import (
    ProductForm, SupplierForm, CustomerForm,
    PurchaseInvoiceForm, SaleInvoiceForm, OrderForm, OrderItemForm,
    EmployeeForm, EmployeeUserForm, RoleForm, PermissionForm,
    SaleReturnForm, SaleReturnItemForm, PurchaseReturnForm, PurchaseReturnItemForm,
    RevenueForm, ExpenseForm, RevenueCategoryForm, ExpenseCategoryForm
)


@login_required
def dashboard(request):
    """لوحة التحكم الرئيسية"""
    # إحصائيات عامة
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()

    # إحصائيات مالية
    total_sales = SaleInvoice.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    total_purchases = PurchaseInvoice.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    total_orders_amount = Order.objects.aggregate(
        total=Sum("total_amount")
    )["total"] or Decimal("0")

    # المنتجات منخفضة المخزون
    low_stock_products = Product.objects.filter(
        quantity__lte=F("min_quantity")
    )[:10]
    low_stock_count = low_stock_products.count()

    # قيمة المخزون الإجمالية
    inventory_value = sum(
        product.total_value for product in Product.objects.all()
    )

    # متوسط قيمة المنتج
    average_product_value = inventory_value / total_products if total_products > 0 else 0

    # فواتير اليوم
    today = timezone.now().date()
    today_invoices = (
            SaleInvoice.objects.filter(date__date=today).count() +
            PurchaseInvoice.objects.filter(date__date=today).count()
    )

    # آخر الفواتير والطلبات
    recent_sales = SaleInvoice.objects.select_related("customer")[:5]
    recent_purchases = PurchaseInvoice.objects.select_related("supplier")[:5]
    recent_orders = Order.objects.select_related("customer")[:5]

    context = {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_customers": total_customers,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_purchases": total_purchases,
        "total_orders_amount": total_orders_amount,
        "low_stock_count": low_stock_count,
        "low_stock_products": low_stock_products,
        "inventory_value": inventory_value,
        "average_product_value": average_product_value,
        "today_invoices": today_invoices,
        "recent_sales": recent_sales,
        "recent_purchases": recent_purchases,
        "recent_orders": recent_orders,
        "today": today,
    }

    return render(request, "inventory/dashboard.html", context)


@login_required
def employee_dashboard(request):
    """لوحة تحكم خاصة بالموظفين العاديين"""
    context = {
        'title': 'لوحة الموظف'
    }
    return render(request, "inventory/employee_dashboard.html", context)


# ========== عروض المنتجات ==========

@login_required
def product_list(request):
    """قائمة المنتجات مع البحث والفلترة"""
    products = Product.objects.select_related("supplier").all()
    suppliers = Supplier.objects.all()

    # البحث
    search = request.GET.get("search")
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(supplier__name__icontains=search)
        )

    # فلترة حسب المورد
    supplier_id = request.GET.get("supplier")
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    # فلترة حسب حالة المخزون
    stock_status = request.GET.get("stock_status")
    if stock_status == "low":
        products = products.filter(quantity__lte=F("min_quantity"))
    elif stock_status == "out":
        products = products.filter(quantity=0)

    context = {
        "products": products,
        "suppliers": suppliers,
    }

    return render(request, "inventory/product_list.html", context)


@login_required
def product_detail(request, pk):
    """تفاصيل المنتج"""
    product = get_object_or_404(Product, pk=pk)

    # آخر المعاملات على هذا المنتج
    recent_purchases = PurchaseInvoiceItem.objects.filter(
        product=product
    ).select_related("invoice__supplier")[:10]

    recent_sales = SaleInvoiceItem.objects.filter(
        product=product
    ).select_related("invoice__customer")[:10]

    context = {
        "product": product,
        "recent_purchases": recent_purchases,
        "recent_sales": recent_sales,
    }

    return render(request, "inventory/product_detail.html", context)


@login_required
def product_barcodes(request):
    """صفحة عرض باركودات المنتجات"""
    products = Product.objects.select_related('supplier').all()
    suppliers = Supplier.objects.all()

    # البحث
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(barcode_data__icontains=search)
        )

    # فلترة حسب المورد
    supplier_id = request.GET.get('supplier')
    if supplier_id:
        products = products.filter(supplier_id=supplier_id)

    context = {
        'products': products,
        'suppliers': suppliers,
        'title': 'باركودات المنتجات'
    }
    return render(request, "inventory/product_barcodes.html", context)


# ========== إدارة الإيرادات ==========

@login_required
def revenue_list(request):
    """قائمة الإيرادات"""
    revenues = Revenue.objects.select_related('category', 'created_by', 'sale_invoice').all()

    # البحث
    search = request.GET.get('search')
    if search:
        revenues = revenues.filter(
            Q(title__icontains=search) |
            Q(reference_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(description__icontains=search)
        )

    # فلترة حسب الفئة
    category_id = request.GET.get('category')
    if category_id:
        revenues = revenues.filter(category_id=category_id)

    # فلترة حسب النوع
    revenue_type = request.GET.get('revenue_type')
    if revenue_type:
        revenues = revenues.filter(revenue_type=revenue_type)

    # فلترة حسب التاريخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        revenues = revenues.filter(date__gte=date_from)
    if date_to:
        revenues = revenues.filter(date__lte=date_to)

    # إحصائيات
    total_amount = revenues.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'revenues': revenues,
        'categories': RevenueCategory.objects.filter(is_active=True),
        'revenue_types': Revenue.REVENUE_TYPES,
        'total_amount': total_amount,
        'title': 'إدارة الإيرادات'
    }
    return render(request, "inventory/revenue_list.html", context)


@login_required
def revenue_create(request):
    """إضافة إيراد جديد"""
    if request.method == 'POST':
        form = RevenueForm(request.POST)
        if form.is_valid():
            revenue = form.save(commit=False)
            revenue.created_by = request.user
            revenue.save()
            messages.success(request, f'تم إضافة الإيراد {revenue.reference_number} بنجاح')
            return redirect('revenue_detail', pk=revenue.pk)
    else:
        form = RevenueForm()

    context = {
        'form': form,
        'title': 'إضافة إيراد جديد'
    }
    return render(request, "inventory/revenue_form.html", context)


@login_required
def revenue_detail(request, pk):
    """تفاصيل الإيراد"""
    revenue = get_object_or_404(Revenue, pk=pk)

    context = {
        'revenue': revenue,
        'title': f'تفاصيل الإيراد {revenue.reference_number}'
    }
    return render(request, "inventory/revenue_detail.html", context)


@login_required
def revenue_edit(request, pk):
    """تعديل الإيراد"""
    revenue = get_object_or_404(Revenue, pk=pk)

    if request.method == 'POST':
        form = RevenueForm(request.POST, instance=revenue)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الإيراد {revenue.reference_number} بنجاح')
            return redirect('revenue_detail', pk=revenue.pk)
    else:
        form = RevenueForm(instance=revenue)

    context = {
        'form': form,
        'revenue': revenue,
        'title': f'تعديل الإيراد {revenue.reference_number}'
    }
    return render(request, "inventory/revenue_form.html", context)


@login_required
def revenue_delete(request, pk):
    """حذف الإيراد"""
    revenue = get_object_or_404(Revenue, pk=pk)

    if revenue.sale_invoice:
        messages.error(request, 'لا يمكن حذف إيراد مرتبط بفاتورة مبيعات')
        return redirect('revenue_detail', pk=pk)

    revenue_ref = revenue.reference_number
    revenue.delete()
    messages.success(request, f'تم حذف الإيراد {revenue_ref} بنجاح')
    return redirect('revenue_list')


# ========== إدارة المصروفات ==========

@login_required
def expense_list(request):
    """قائمة المصروفات"""
    expenses = Expense.objects.select_related('category', 'created_by', 'purchase_invoice').all()

    # البحث
    search = request.GET.get('search')
    if search:
        expenses = expenses.filter(
            Q(title__icontains=search) |
            Q(reference_number__icontains=search) |
            Q(supplier_name__icontains=search) |
            Q(description__icontains=search)
        )

    # فلترة حسب الفئة
    category_id = request.GET.get('category')
    if category_id:
        expenses = expenses.filter(category_id=category_id)

    # فلترة حسب النوع
    expense_type = request.GET.get('expense_type')
    if expense_type:
        expenses = expenses.filter(expense_type=expense_type)

    # فلترة حسب التاريخ
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    # إحصائيات
    total_amount = expenses.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'expenses': expenses,
        'categories': ExpenseCategory.objects.filter(is_active=True),
        'expense_types': Expense.EXPENSE_TYPES,
        'total_amount': total_amount,
        'title': 'إدارة المصروفات'
    }
    return render(request, "inventory/expense_list.html", context)


@login_required
def expense_create(request):
    """إضافة مصروف جديد"""
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.created_by = request.user
            expense.save()
            messages.success(request, f'تم إضافة المصروف {expense.reference_number} بنجاح')
            return redirect('expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm()

    context = {
        'form': form,
        'title': 'إضافة مصروف جديد'
    }
    return render(request, "inventory/expense_form.html", context)


@login_required
def expense_detail(request, pk):
    """تفاصيل المصروف"""
    expense = get_object_or_404(Expense, pk=pk)

    context = {
        'expense': expense,
        'title': f'تفاصيل المصروف {expense.reference_number}'
    }
    return render(request, "inventory/expense_detail.html", context)


@login_required
def expense_edit(request, pk):
    """تعديل المصروف"""
    expense = get_object_or_404(Expense, pk=pk)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث المصروف {expense.reference_number} بنجاح')
            return redirect('expense_detail', pk=expense.pk)
    else:
        form = ExpenseForm(instance=expense)

    context = {
        'form': form,
        'expense': expense,
        'title': f'تعديل المصروف {expense.reference_number}'
    }
    return render(request, "inventory/expense_form.html", context)


@login_required
def expense_delete(request, pk):
    """حذف المصروف"""
    expense = get_object_or_404(Expense, pk=pk)

    if expense.purchase_invoice:
        messages.error(request, 'لا يمكن حذف مصروف مرتبط بفاتورة مشتريات')
        return redirect('expense_detail', pk=pk)

    expense_ref = expense.reference_number
    expense.delete()
    messages.success(request, f'تم حذف المصروف {expense_ref} بنجاح')
    return redirect('expense_list')


# ========== إدارة فئات الإيرادات والمصروفات ==========

@login_required
def revenue_category_list(request):
    """قائمة فئات الإيرادات"""
    if request.method == 'POST':
        action = request.POST.get('action')
        category_id = request.POST.get('category_id')

        if action == 'edit' and category_id:
            try:
                category = RevenueCategory.objects.get(id=category_id)
                category.name = request.POST.get('name', category.name)
                category.description = request.POST.get('description', category.description)
                category.is_active = 'is_active' in request.POST
                category.save()
                messages.success(request, f'تم تحديث الفئة {category.name} بنجاح')
            except RevenueCategory.DoesNotExist:
                messages.error(request, 'الفئة غير موجودة')

        elif action == 'delete' and category_id:
            try:
                category = RevenueCategory.objects.get(id=category_id)
                if category.revenue_set.count() == 0:
                    category_name = category.name
                    category.delete()
                    messages.success(request, f'تم حذف الفئة {category_name} بنجاح')
                else:
                    messages.error(request, 'لا يمكن حذف فئة مرتبطة بإيرادات')
            except RevenueCategory.DoesNotExist:
                messages.error(request, 'الفئة غير موجودة')

        return redirect('revenue_category_list')

    categories = RevenueCategory.objects.all()

    context = {
        'categories': categories,
        'title': 'فئات الإيرادات'
    }
    return render(request, "inventory/revenue_category_list.html", context)


@login_required
def revenue_category_create(request):
    """إضافة فئة إيراد جديدة"""
    if request.method == 'POST':
        form = RevenueCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم إضافة فئة الإيراد {category.name} بنجاح')
            return redirect('revenue_category_list')
    else:
        form = RevenueCategoryForm()

    context = {
        'form': form,
        'title': 'إضافة فئة إيراد جديدة'
    }
    return render(request, "inventory/revenue_category_form.html", context)


@login_required
def expense_category_list(request):
    """قائمة فئات المصروفات"""
    if request.method == 'POST':
        action = request.POST.get('action')
        category_id = request.POST.get('category_id')

        if action == 'edit' and category_id:
            try:
                category = ExpenseCategory.objects.get(id=category_id)
                category.name = request.POST.get('name', category.name)
                category.description = request.POST.get('description', category.description)
                category.is_active = 'is_active' in request.POST
                category.save()
                messages.success(request, f'تم تحديث الفئة {category.name} بنجاح')
            except ExpenseCategory.DoesNotExist:
                messages.error(request, 'الفئة غير موجودة')

        elif action == 'delete' and category_id:
            try:
                category = ExpenseCategory.objects.get(id=category_id)
                if category.expense_set.count() == 0:
                    category_name = category.name
                    category.delete()
                    messages.success(request, f'تم حذف الفئة {category_name} بنجاح')
                else:
                    messages.error(request, 'لا يمكن حذف فئة مرتبطة بمصروفات')
            except ExpenseCategory.DoesNotExist:
                messages.error(request, 'الفئة غير موجودة')

        return redirect('expense_category_list')

    categories = ExpenseCategory.objects.all()

    context = {
        'categories': categories,
        'title': 'فئات المصروفات'
    }
    return render(request, "inventory/expense_category_list.html", context)


@login_required
def expense_category_create(request):
    """إضافة فئة مصروف جديدة"""
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'تم إضافة فئة المصروف {category.name} بنجاح')
            return redirect('expense_category_list')
    else:
        form = ExpenseCategoryForm()

    context = {
        'form': form,
        'title': 'إضافة فئة مصروف جديدة'
    }
    return render(request, "inventory/expense_category_form.html", context)


@login_required
def product_create(request):
    """إضافة منتج جديد"""
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المنتج بنجاح")
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "inventory/product_form.html", {
        "form": form,
        "title": "إضافة منتج جديد"
    })


@login_required
def product_edit(request, pk):
    """تعديل منتج"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المنتج بنجاح")
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, "inventory/product_form.html", {
        "form": form,
        "product": product,
        "title": f"تعديل المنتج: {product.name}"
    })


@login_required
def product_delete(request, pk):
    """حذف منتج"""
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        product_name = product.name
        product.delete()
        messages.success(request, f"تم حذف المنتج \"{product_name}\" بنجاح")
        return redirect("product_list")

    return render(request, "inventory/product_confirm_delete.html", {
        "product": product
    })


# ========== عروض الموردين ==========

@login_required
def supplier_list(request):
    """قائمة الموردين"""
    suppliers = Supplier.objects.all()

    # البحث
    search = request.GET.get("search")
    if search:
        suppliers = suppliers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    return render(request, "inventory/supplier_list.html", {
        "suppliers": suppliers
    })


@login_required
def supplier_create(request):
    """إضافة مورد جديد"""
    if request.method == "POST":
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة المورد بنجاح")
            return redirect("supplier_list")
    else:
        form = SupplierForm()

    return render(request, "inventory/supplier_form.html", {
        "form": form,
        "title": "إضافة مورد جديد"
    })


@login_required
def supplier_edit(request, pk):
    """تعديل مورد"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث المورد بنجاح")
            return redirect("supplier_list")
    else:
        form = SupplierForm(instance=supplier)

    return render(request, "inventory/supplier_form.html", {
        "form": form,
        "supplier": supplier,
        "title": f"تعديل المورد: {supplier.name}"
    })


@login_required
def supplier_delete(request, pk):
    """حذف مورد"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == "POST":
        supplier_name = supplier.name
        supplier.delete()
        messages.success(request, f"تم حذف المورد \"{supplier_name}\" بنجاح")
        return redirect("supplier_list")

    return render(request, "inventory/supplier_confirm_delete.html", {
        "supplier": supplier
    })


# ========== عروض العملاء ==========

@login_required
def customer_list(request):
    """قائمة العملاء"""
    customers = Customer.objects.all()

    # البحث
    search = request.GET.get("search")
    if search:
        customers = customers.filter(
            Q(name__icontains=search) |
            Q(phone__icontains=search) |
            Q(email__icontains=search)
        )

    return render(request, "inventory/customer_list.html", {
        "customers": customers
    })


@login_required
def customer_create(request):
    """إضافة عميل جديد"""
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "تم إضافة العميل بنجاح")
            return redirect("customer_list")
    else:
        form = CustomerForm()

    return render(request, "inventory/customer_form.html", {
        "form": form,
        "title": "إضافة عميل جديد"
    })


@login_required
def customer_edit(request, pk):
    """تعديل عميل"""
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "تم تحديث العميل بنجاح")
            return redirect("customer_list")
    else:
        form = CustomerForm(instance=customer)

    return render(request, "inventory/customer_form.html", {
        "form": form,
        "customer": customer,
        "title": f"تعديل العميل: {customer.name}"
    })


@login_required
def customer_delete(request, pk):
    """حذف عميل"""
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == "POST":
        customer_name = customer.name
        customer.delete()
        messages.success(request, f"تم حذف العميل \"{customer_name}\" بنجاح")
        return redirect("customer_list")

    return render(request, "inventory/customer_confirm_delete.html", {
        "customer": customer
    })


# ========== عروض فواتير البيع ==========

@login_required
def sale_invoice_list(request):
    """قائمة فواتير البيع"""
    invoices = SaleInvoice.objects.select_related("customer", "created_by").all()

    # البحث والفلترة
    search = request.GET.get("search")
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(customer__name__icontains=search)
        )

    return render(request, "inventory/sale_invoice_list.html", {
        "invoices": invoices
    })


from decimal import Decimal
from .models import SaleInvoice, SaleInvoiceItem, Product


@login_required
def sale_invoice_create(request):
    products = Product.objects.all()

    if request.method == "POST":
        form = SaleInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()

            product_ids = request.POST.getlist("product")
            quantities = request.POST.getlist("quantity")
            prices = request.POST.getlist("price")

            total_amount = Decimal("0")

            for i in range(len(product_ids)):
                try:
                    product = Product.objects.get(pk=product_ids[i])
                    quantity = int(quantities[i])
                    unit_price = Decimal(prices[i])
                except:
                    continue

                if quantity <= 0 or unit_price <= 0:
                    continue

                if product.quantity < quantity:
                    messages.error(request,
                                   f"❌ الكمية المطلوبة للمنتج {product.name} غير متوفرة (المتوفر: {product.quantity})")
                    return redirect("sale_invoice_create")

                total_price = quantity * unit_price

                # إنشاء عنصر الفاتورة
                SaleInvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )

                # خصم من المخزون
                product.quantity -= quantity
                product.save()

                total_amount += total_price

            invoice.total_amount = total_amount
            invoice.save()

            messages.success(request, "✅ تم إنشاء فاتورة البيع بنجاح")
            return redirect("sale_invoice_detail", pk=invoice.pk)
    else:
        form = SaleInvoiceForm()

    return render(request, "inventory/sale_invoice_form.html", {
        "form": form,
        "products": products,
        "title": "إنشاء فاتورة بيع"
    })


@login_required
def purchase_invoice_list(request):
    """قائمة فواتير الشراء مع المنتجات"""
    invoices = PurchaseInvoice.objects.select_related("supplier", "created_by").prefetch_related("items__product")

    # البحث والفلترة
    search = request.GET.get("search")
    if search:
        invoices = invoices.filter(
            Q(invoice_number__icontains=search) |
            Q(supplier__name__icontains=search)
        )

    return render(request, "inventory/purchase_invoice_list.html", {
        "invoices": invoices
    })


from decimal import Decimal
from django.contrib import messages
from .models import PurchaseInvoice, PurchaseInvoiceItem, Product
from .forms import PurchaseInvoiceForm


@login_required
def purchase_invoice_create(request):
    """إنشاء فاتورة شراء جديدة مع إضافة المنتجات"""
    products = Product.objects.all()

    if request.method == "POST":
        form = PurchaseInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.created_by = request.user
            invoice.save()

            # استلام القيم من النموذج
            product_ids = request.POST.getlist("product")
            quantities = request.POST.getlist("quantity")
            prices = request.POST.getlist("price")

            total_amount = Decimal("0")

            for i in range(len(product_ids)):
                try:
                    product = Product.objects.get(pk=product_ids[i])
                    quantity = int(quantities[i])
                    unit_price = Decimal(prices[i])
                except:
                    continue  # تجاوز العنصر إذا فيه مشكلة

                if quantity <= 0 or unit_price <= 0:
                    continue

                total_price = quantity * unit_price

                # إنشاء عنصر الفاتورة
                PurchaseInvoiceItem.objects.create(
                    invoice=invoice,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    total_price=total_price
                )

                # تحديث كمية المنتج في المخزون
                product.quantity += quantity
                product.save()

                total_amount += total_price

            invoice.total_amount = total_amount
            invoice.save()

            messages.success(request, "✅ تم إنشاء فاتورة الشراء بنجاح")
            return redirect("purchase_invoice_detail", pk=invoice.pk)
    else:
        form = PurchaseInvoiceForm()

    return render(request, "inventory/purchase_invoice_form.html", {
        "form": form,
        "products": products,
        "title": "إنشاء فاتورة شراء جديدة"
    })


# ========== عروض الطلبات ==========

@login_required
def order_list(request):
    """قائمة الطلبات مع البحث والفلترة"""
    orders = Order.objects.select_related("customer", "created_by").all()

    search = request.GET.get("search")
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer__name__icontains=search)
        )

    status_filter = request.GET.get("status")
    if status_filter:
        orders = orders.filter(status=status_filter)

    # حساب إحصائيات الطلبات حسب الحالة
    all_orders = Order.objects.all()
    pending_count = all_orders.filter(status='pending').count()
    processing_count = all_orders.filter(status='processing').count()
    shipped_count = all_orders.filter(status='shipped').count()
    delivered_count = all_orders.filter(status='delivered').count()
    cancelled_count = all_orders.filter(status='cancelled').count()

    context = {
        "orders": orders,
        "status_choices": Order.STATUS_CHOICES,
        "pending_count": pending_count,
        "processing_count": processing_count,
        "shipped_count": shipped_count,
        "delivered_count": delivered_count,
        "cancelled_count": cancelled_count,
    }
    return render(request, "inventory/order_list.html", context)


@login_required
def order_create(request):
    """إنشاء طلب جديد"""
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            messages.success(request, "تم إنشاء الطلب بنجاح")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm()

    return render(request, "inventory/order_form.html", {
        "form": form,
        "title": "إنشاء طلب جديد"
    })


@login_required
def order_detail(request, pk):
    """تفاصيل الطلب"""
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.all()

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "inventory/order_detail.html", context)


@login_required
def order_edit(request, pk):
    """تعديل الطلب"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            messages.success(request, "تم تحديث الطلب بنجاح")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderForm(instance=order)

    context = {
        "form": form,
        "order": order,
        "title": f"تعديل الطلب: {order.order_number}"
    }
    return render(request, "inventory/order_form.html", context)


@login_required
def order_delete(request, pk):
    """حذف الطلب"""
    order = get_object_or_404(Order, pk=pk)

    if request.method == "POST":
        order_number = order.order_number
        order.delete()
        messages.success(request, f"تم حذف الطلب \"{order_number}\" بنجاح")
        return redirect("order_list")

    return render(request, "inventory/order_confirm_delete.html", {
        "order": order
    })


@login_required
def order_item_create(request, order_pk):
    """إضافة عنصر إلى الطلب"""
    order = get_object_or_404(Order, pk=order_pk)
    if request.method == "POST":
        form = OrderItemForm(request.POST)
        if form.is_valid():
            order_item = form.save(commit=False)
            order_item.order = order
            order_item.save()
            # تحديث إجمالي الطلب
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            messages.success(request, "تم إضافة المنتج إلى الطلب بنجاح")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderItemForm()

    context = {
        "form": form,
        "order": order,
        "title": f"إضافة منتج للطلب {order.order_number}"
    }
    return render(request, "inventory/order_item_form.html", context)


@login_required
def order_item_edit(request, order_pk, pk):
    """تعديل عنصر في الطلب"""
    order = get_object_or_404(Order, pk=order_pk)
    order_item = get_object_or_404(OrderItem, pk=pk, order=order)

    if request.method == "POST":
        form = OrderItemForm(request.POST, instance=order_item)
        if form.is_valid():
            order_item = form.save()
            # تحديث إجمالي الطلب
            order.total_amount = sum(item.total_price for item in order.items.all())
            order.save()
            messages.success(request, "تم تحديث المنتج في الطلب بنجاح")
            return redirect("order_detail", pk=order.pk)
    else:
        form = OrderItemForm(instance=order_item)

    context = {
        "form": form,
        "order": order,
        "order_item": order_item,
        "title": f"تعديل منتج في الطلب {order.order_number}"
    }
    return render(request, "inventory/order_item_form.html", context)


@login_required
def order_item_delete(request, order_pk, pk):
    """حذف عنصر من الطلب"""
    order = get_object_or_404(Order, pk=order_pk)
    order_item = get_object_or_404(OrderItem, pk=pk, order=order)

    if request.method == "POST":
        order_item.delete()
        # تحديث إجمالي الطلب
        order.total_amount = sum(item.total_price for item in order.items.all())
        order.save()
        messages.success(request, "تم حذف المنتج من الطلب بنجاح")
        return redirect("order_detail", pk=order.pk)

    return render(request, "inventory/order_item_confirm_delete.html", {
        "order": order,
        "order_item": order_item
    })


# ========== عروض التقارير ==========

@login_required
def reports(request):
    """صفحة التقارير"""
    # إحصائيات عامة
    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_customers = Customer.objects.count()

    # تقرير المبيعات الشهرية
    current_month = timezone.now().replace(day=1)
    monthly_sales = SaleInvoice.objects.filter(
        date__gte=current_month
    ).aggregate(
        total=Sum("total_amount"),
        count=Count("id")
    )

    # تقرير المشتريات الشهرية
    monthly_purchases = PurchaseInvoice.objects.filter(
        date__gte=current_month
    ).aggregate(
        total=Sum("total_amount"),
        count=Count("id")
    )

    # المنتجات الأكثر مبيعاً
    top_selling_products = SaleInvoiceItem.objects.values(
        "product__name"
    ).annotate(
        total_quantity=Sum("quantity"),
        total_revenue=Sum("total_price")
    ).order_by("-total_quantity")[:10]

    # المنتجات منخفضة المخزون
    low_stock_products = Product.objects.filter(
        quantity__lte=F("min_quantity")
    )

    # بيانات للرسم البياني
    # مبيعات آخر 6 أشهر
    from datetime import datetime, timedelta
    try:
        from dateutil.relativedelta import relativedelta
    except ImportError:
        # إذا لم تكن dateutil متوفرة، استخدم حل بديل
        def relativedelta(months=0):
            class RelativeDelta:
                def __init__(self, months):
                    self.months = months
            return RelativeDelta(months)

    sales_chart_data = []
    purchases_chart_data = []
    months_labels = []

    for i in range(6):
        # حساب بداية الشهر
        current_date = timezone.now()
        if 'relativedelta' in locals() and hasattr(relativedelta(months=1), 'months'):
            month_start = (current_date.replace(day=1) - relativedelta(months=i))
            month_end = month_start + relativedelta(months=1) - timedelta(days=1)
        else:
            # حل بديل بدون dateutil
            year = current_date.year
            month = current_date.month - i
            while month <= 0:
                month += 12
                year -= 1
            month_start = current_date.replace(year=year, month=month, day=1)
            # حساب نهاية الشهر
            if month == 12:
                month_end = current_date.replace(year=year+1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = current_date.replace(year=year, month=month+1, day=1) - timedelta(days=1)

        month_sales = SaleInvoice.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum("total_amount"))['total'] or 0

        month_purchases = PurchaseInvoice.objects.filter(
            date__gte=month_start,
            date__lte=month_end
        ).aggregate(total=Sum("total_amount"))['total'] or 0

        sales_chart_data.append(float(month_sales))
        purchases_chart_data.append(float(month_purchases))

        # تنسيق اسم الشهر باللغة العربية
        month_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل",
            5: "مايو", 6: "يونيو", 7: "يوليو", 8: "أغسطس",
            9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        month_name = month_names.get(month_start.month, month_start.strftime("%B"))
        months_labels.append(f"{month_name} {month_start.year}")

    # عكس البيانات لتظهر من الأقدم للأحدث
    sales_chart_data.reverse()
    purchases_chart_data.reverse()
    months_labels.reverse()

    # تحويل البيانات إلى JSON
    import json

    context = {
        "total_products": total_products,
        "total_suppliers": total_suppliers,
        "total_customers": total_customers,
        "monthly_sales": monthly_sales,
        "monthly_purchases": monthly_purchases,
        "top_selling_products": top_selling_products,
        "low_stock_products": low_stock_products,
        "current_month": current_month,
        "sales_chart_data": json.dumps(sales_chart_data),
        "purchases_chart_data": json.dumps(purchases_chart_data),
        "months_labels": json.dumps(months_labels),
    }

    return render(request, "inventory/reports.html", context)


# ========== عروض تسجيل الدخول المخصصة ==========

class CustomLoginView(LoginView):
    """عرض تسجيل دخول مخصص مع إعادة توجيه بناءً على نوع المستخدم"""
    template_name = 'registration/login.html'

    def get_success_url(self):
        """تحديد صفحة إعادة التوجيه بناءً على نوع المستخدم"""
        user = self.request.user

        # المدير العام يذهب للوحة التحكم
        if user.is_superuser:
            messages.success(self.request, f'مرحباً بك {user.get_full_name() or user.username} (مدير عام)')
            return reverse_lazy('dashboard')

        try:
            employee = user.employee_profile

            # المدير يذهب للوحة التحكم مع رسالة ترحيب
            if employee.is_manager:
                messages.success(
                    self.request,
                    f'مرحباً بك {user.get_full_name() or user.username} ({employee.role.name})'
                )
                return reverse_lazy('dashboard')

            # الموظف العادي يذهب للوحة الموظف
            else:
                messages.success(
                    self.request,
                    f'مرحباً بك {user.get_full_name() or user.username} ({employee.role.name if employee.role else "موظف"})'
                )
                return reverse_lazy('employee_dashboard')

        except:
            # في حالة عدم وجود ملف موظف، يذهب للوحة التحكم
            messages.success(self.request, f'مرحباً بك {user.get_full_name() or user.username}')
            return reverse_lazy('dashboard')

    def form_valid(self, form):
        """معالجة نجح تسجيل الدخول"""
        response = super().form_valid(form)

        # تسجيل محاولة تسجيل الدخول الناجحة
        user = self.request.user
        try:
            employee = user.employee_profile
            # يمكن إضافة تسجيل في قاعدة البيانات هنا
        except:
            pass

        return response

    def form_invalid(self, form):
        """معالجة فشل تسجيل الدخول"""
        messages.error(self.request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
        return super().form_invalid(form)


# ========== عروض المرتجعات ==========

@login_required
def sale_return_create(request, invoice_id):
    """إنشاء مرتجع مبيعات"""
    original_invoice = get_object_or_404(SaleInvoice, id=invoice_id)

    if request.method == 'POST':
        form = SaleReturnForm(request.POST)

        if form.is_valid():
            try:
                # إنشاء مرتجع المبيعات
                sale_return = form.save(commit=False)
                sale_return.original_invoice = original_invoice
                sale_return.created_by = request.user
                sale_return.save()

                total_amount = 0
                returned_items_count = 0

                # معالجة عناصر المرتجع
                for item in original_invoice.items.all():
                    returned_quantity_str = request.POST.get(f'returned_quantity_{item.id}')

                    if returned_quantity_str:
                        try:
                            returned_quantity = int(returned_quantity_str)

                            if returned_quantity > 0:
                                # التحقق من صحة الكمية
                                if returned_quantity <= item.quantity:
                                    # إنشاء عنصر المرتجع
                                    return_item = SaleReturnItem.objects.create(
                                        sale_return=sale_return,
                                        original_item=item,
                                        product=item.product,
                                        returned_quantity=returned_quantity,
                                        unit_price=item.unit_price
                                    )
                                    total_amount += return_item.total_price
                                    returned_items_count += 1

                                    # إضافة الكمية المرتجعة إلى المخزون
                                    item.product.quantity += returned_quantity
                                    item.product.save()

                                    messages.info(request, f'تم إضافة {returned_quantity} من {item.product.name} إلى المخزون')
                                else:
                                    messages.warning(request, f'الكمية المرتجعة لـ {item.product.name} أكبر من الكمية الأصلية')
                        except ValueError:
                            messages.warning(request, f'كمية غير صحيحة لـ {item.product.name}')

                # تحديث إجمالي المرتجع
                sale_return.total_amount = total_amount
                sale_return.save()

                if returned_items_count > 0:
                    messages.success(request, f'تم إنشاء مرتجع المبيعات #{sale_return.return_number} بنجاح')
                    messages.success(request, f'تم إرجاع {returned_items_count} منتج بقيمة إجمالية {total_amount:.2f} ر.س')
                    return redirect('sale_return_detail', pk=sale_return.pk)
                else:
                    # حذف المرتجع إذا لم تكن هناك عناصر مرتجعة
                    sale_return.delete()
                    messages.error(request, 'يجب تحديد كمية مرتجعة لمنتج واحد على الأقل')
                    return redirect('sale_invoice_detail', pk=original_invoice.pk)

            except Exception as e:
                messages.error(request, f'حدث خطأ أثناء إنشاء المرتجع: {str(e)}')
                return redirect('sale_invoice_detail', pk=original_invoice.pk)
        else:
            # عرض أخطاء النموذج
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'خطأ في {field}: {error}')
    else:
        form = SaleReturnForm()

    context = {
        'form': form,
        'original_invoice': original_invoice,
        'title': f'إنشاء مرتجع لفاتورة #{original_invoice.invoice_number}'
    }
    return render(request, 'inventory/sale_return_create.html', context)


@login_required
def sale_return_detail(request, pk):
    """تفاصيل مرتجع المبيعات"""
    sale_return = get_object_or_404(SaleReturn, pk=pk)

    context = {
        'sale_return': sale_return,
        'title': f'مرتجع مبيعات #{sale_return.return_number}'
    }
    return render(request, 'inventory/sale_return_detail.html', context)


@login_required
def sale_return_list(request):
    """قائمة مرتجعات المبيعات"""
    returns = SaleReturn.objects.select_related('original_invoice', 'created_by').all()

    # البحث
    search = request.GET.get('search')
    if search:
        returns = returns.filter(
            Q(return_number__icontains=search) |
            Q(original_invoice__invoice_number__icontains=search) |
            Q(reason__icontains=search)
        )

    context = {
        'returns': returns,
        'title': 'مرتجعات المبيعات'
    }
    return render(request, 'inventory/sale_return_list.html', context)


@login_required
def purchase_return_create(request, invoice_id):
    """إنشاء مرتجع مشتريات"""
    original_invoice = get_object_or_404(PurchaseInvoice, id=invoice_id)

    if request.method == 'POST':
        form = PurchaseReturnForm(request.POST)

        if form.is_valid():
            # إنشاء مرتجع المشتريات
            purchase_return = form.save(commit=False)
            purchase_return.original_invoice = original_invoice
            purchase_return.created_by = request.user
            purchase_return.save()

            total_amount = 0

            # معالجة عناصر المرتجع
            for item in original_invoice.items.all():
                returned_quantity = request.POST.get(f'returned_quantity_{item.id}')

                if returned_quantity and int(returned_quantity) > 0:
                    returned_quantity = int(returned_quantity)

                    # التحقق من صحة الكمية
                    if returned_quantity <= item.quantity and returned_quantity <= item.product.quantity:
                        # إنشاء عنصر المرتجع
                        return_item = PurchaseReturnItem.objects.create(
                            purchase_return=purchase_return,
                            original_item=item,
                            product=item.product,
                            returned_quantity=returned_quantity,
                            unit_price=item.unit_price
                        )
                        total_amount += return_item.total_price

            # تحديث إجمالي المرتجع
            purchase_return.total_amount = total_amount
            purchase_return.save()

            messages.success(request, f'تم إنشاء مرتجع المشتريات #{purchase_return.return_number} بنجاح')
            return redirect('purchase_return_detail', pk=purchase_return.pk)
    else:
        form = PurchaseReturnForm()

    context = {
        'form': form,
        'original_invoice': original_invoice,
        'title': f'إنشاء مرتجع لفاتورة #{original_invoice.invoice_number}'
    }
    return render(request, 'inventory/purchase_return_create.html', context)


@login_required
def purchase_return_detail(request, pk):
    """تفاصيل مرتجع المشتريات"""
    purchase_return = get_object_or_404(PurchaseReturn, pk=pk)

    context = {
        'purchase_return': purchase_return,
        'title': f'مرتجع مشتريات #{purchase_return.return_number}'
    }
    return render(request, 'inventory/purchase_return_detail.html', context)


@login_required
def purchase_return_list(request):
    """قائمة مرتجعات المشتريات"""
    returns = PurchaseReturn.objects.select_related('original_invoice', 'created_by').all()

    # البحث
    search = request.GET.get('search')
    if search:
        returns = returns.filter(
            Q(return_number__icontains=search) |
            Q(original_invoice__invoice_number__icontains=search) |
            Q(reason__icontains=search)
        )

    context = {
        'returns': returns,
        'title': 'مرتجعات المشتريات'
    }
    return render(request, 'inventory/purchase_return_list.html', context)


# ========== API للبيانات الديناميكية ==========

@login_required
def get_product_price(request, product_id):
    """الحصول على سعر المنتج"""
    try:
        product = Product.objects.get(id=product_id)
        return JsonResponse({
            "price": float(product.price),
            "quantity": product.quantity,
            "name": product.name
        })
    except Product.DoesNotExist:
        return JsonResponse({"error": "المنتج غير موجود"}, status=404)


@login_required
def check_product_availability(request, product_id, quantity):
    """التحقق من توفر الكمية المطلوبة"""
    try:
        product = Product.objects.get(id=product_id)
        available = product.quantity >= int(quantity)
        return JsonResponse({
            "available": available,
            "current_quantity": product.quantity,
            "requested_quantity": int(quantity)
        })
    except Product.DoesNotExist:
        return JsonResponse({"error": "المنتج غير موجود"}, status=404)
    except ValueError:
        return JsonResponse({"error": "كمية غير صحيحة"}, status=400)


@login_required
def sale_invoice_detail(request, pk):
    """عرض تفاصيل فاتورة البيع"""
    invoice = get_object_or_404(SaleInvoice, pk=pk)
    items = SaleInvoiceItem.objects.filter(invoice=invoice)
    return render(request, "inventory/sale_invoice_detail.html", {
        "invoice": invoice,
        "items": items
    })


@login_required
def purchase_invoice_detail(request, pk):
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    items = invoice.items.all()  # ✅ استخدم related_name مباشرة

    return render(request, "inventory/purchase_invoice_detail.html", {
        "invoice": invoice,
        "items": items,
    })


@login_required
def sale_invoice_print(request, pk):
    invoice = get_object_or_404(SaleInvoice, pk=pk)
    items = invoice.items.all()  # تأكد أن related_name='items' مستخدم في الموديل

    return render(request, "inventory/sale_invoice_print.html", {
        "invoice": invoice,
        "items": items
    })


@login_required
def purchase_invoice_print(request, pk):
    """طباعة فاتورة الشراء"""
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    items = invoice.items.all()

    return render(request, "inventory/purchase_invoice_print.html", {
        "invoice": invoice,
        "items": items
    })


# ========== عروض إدارة الموظفين (للمدير والأدمن فقط) ==========

@admin_required
def employee_list(request):
    """قائمة الموظفين - للمدير والأدمن فقط"""
    # تحقق من وجود الجدول قبل الاستعلام
    try:
        # محاولة الوصول إلى جدول الموظفين
        employees = Employee.objects.select_related('user', 'role').all()

        # البحث
        search = request.GET.get('search')
        if search:
            employees = employees.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(department__icontains=search)
            )

        # فلترة حسب الحالة
        status_filter = request.GET.get('status')
        if status_filter:
            employees = employees.filter(employment_status=status_filter)

        # فلترة حسب الدور
        role_filter = request.GET.get('role')
        if role_filter:
            employees = employees.filter(role_id=role_filter)

        # إحصائيات
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(employment_status='active').count()
        inactive_employees = Employee.objects.filter(employment_status='inactive').count()

        context = {
            'employees': employees,
            'roles': Role.objects.filter(is_active=True),
            'employment_status_choices': Employee.EMPLOYMENT_STATUS_CHOICES,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': inactive_employees,
            'migration_error': False,
        }
    except Exception as e:
        # في حالة وجود خطأ (مثل عدم وجود الجدول)
        context = {
            'migration_error': True,
            'error_message': str(e),
            'employees': [],
            'roles': [],
            'employment_status_choices': Employee.EMPLOYMENT_STATUS_CHOICES,
            'total_employees': 0,
            'active_employees': 0,
            'inactive_employees': 0,
        }

    return render(request, 'inventory/employee_list.html', context)


@admin_required
def employee_create(request):
    """إضافة موظف جديد - للمدير والأدمن فقط"""
    if request.method == 'POST':
        user_form = EmployeeUserForm(request.POST)
        employee_form = EmployeeForm(request.POST)

        if user_form.is_valid() and employee_form.is_valid():
            # إنشاء المستخدم
            user = user_form.save()

            # إنشاء ملف الموظف
            employee = employee_form.save(commit=False)
            employee.user = user
            employee.save()

            messages.success(request, f'تم إضافة الموظف {user.get_full_name()} بنجاح')
            return redirect('employee_detail', pk=employee.pk)
    else:
        user_form = EmployeeUserForm()
        employee_form = EmployeeForm()

    context = {
        'user_form': user_form,
        'employee_form': employee_form,
        'title': 'إضافة موظف جديد'
    }
    return render(request, 'inventory/employee_form.html', context)


@admin_required
def employee_detail(request, pk):
    """تفاصيل الموظف - للمدير والأدمن فقط"""
    try:
        employee = get_object_or_404(Employee, pk=pk)
        context = {
            'employee': employee,
            'migration_error': False
        }
    except Exception as e:
        # في حالة وجود خطأ (مثل عدم وجود الجدول)
        context = {
            'employee': None,
            'migration_error': True,
            'error_message': str(e)
        }

    return render(request, 'inventory/employee_detail.html', context)


@admin_required
def employee_edit(request, pk):
    """تعديل بيانات الموظف - للمدير والأدمن فقط"""
    try:
        employee = get_object_or_404(Employee, pk=pk)

        if request.method == 'POST':
            employee_form = EmployeeForm(request.POST, instance=employee)

            # تحديث بيانات المستخدم الأساسية
            user = employee.user
            user.first_name = request.POST.get('first_name', user.first_name)
            user.last_name = request.POST.get('last_name', user.last_name)
            user.email = request.POST.get('email', user.email)
            user.save()

            if employee_form.is_valid():
                employee_form.save()
                messages.success(request, f'تم تحديث بيانات الموظف {user.get_full_name()} بنجاح')
                return redirect('employee_detail', pk=employee.pk)
        else:
            employee_form = EmployeeForm(instance=employee)

        context = {
            'employee': employee,
            'employee_form': employee_form,
            'title': f'تعديل بيانات {employee.user.get_full_name()}',
            'migration_error': False
        }
    except Exception as e:
        # في حالة وجود خطأ (مثل عدم وجود الجدول)
        context = {
            'employee': None,
            'migration_error': True,
            'error_message': str(e)
        }

    return render(request, 'inventory/employee_edit.html', context)


@admin_required
def employee_delete(request, pk):
    """حذف الموظف - للمدير والأدمن فقط"""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        user = employee.user
        employee_name = user.get_full_name()

        # حذف الموظف والمستخدم
        employee.delete()
        user.delete()

        messages.success(request, f'تم حذف الموظف {employee_name} بنجاح')
        return redirect('employee_list')

    context = {
        'employee': employee,
    }
    return render(request, 'inventory/employee_confirm_delete.html', context)


# ========== عروض إدارة الأدوار (للمدير والأدمن فقط) ==========

@admin_required
def role_list(request):
    """قائمة الأدوار الوظيفية - للمدير والأدمن فقط"""
    try:
        # محاولة الوصول إلى جدول الأدوار
        roles = Role.objects.prefetch_related('permissions').all()

        # البحث
        search = request.GET.get('search')
        if search:
            roles = roles.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        context = {
            'roles': roles,
            'migration_error': False
        }
    except Exception as e:
        # في حالة وجود خطأ (مثل عدم وجود الجدول)
        context = {
            'roles': [],
            'migration_error': True,
            'error_message': str(e)
        }

    return render(request, 'inventory/role_list.html', context)


@admin_required
def role_create(request):
    """إضافة دور وظيفي جديد - للمدير والأدمن فقط"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, f'تم إضافة الدور {role.name} بنجاح')
            return redirect('role_detail', pk=role.pk)
    else:
        form = RoleForm()

    context = {
        'form': form,
        'title': 'إضافة دور وظيفي جديد'
    }
    return render(request, 'inventory/role_form.html', context)


@admin_required
def role_detail(request, pk):
    """تفاصيل الدور الوظيفي - للمدير والأدمن فقط"""
    role = get_object_or_404(Role, pk=pk)
    employees_count = Employee.objects.filter(role=role).count()

    context = {
        'role': role,
        'employees_count': employees_count,
    }
    return render(request, 'inventory/role_detail.html', context)


@admin_required
def role_edit(request, pk):
    """تعديل الدور الوظيفي - للمدير والأدمن فقط"""
    role = get_object_or_404(Role, pk=pk)

    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f'تم تحديث الدور {role.name} بنجاح')
            return redirect('role_detail', pk=role.pk)
    else:
        form = RoleForm(instance=role)

    context = {
        'form': form,
        'role': role,
        'title': f'تعديل الدور {role.name}'
    }
    return render(request, 'inventory/role_form.html', context)


@admin_required
def role_delete(request, pk):
    """حذف الدور الوظيفي - للمدير والأدمن فقط"""
    role = get_object_or_404(Role, pk=pk)
    employees_count = Employee.objects.filter(role=role).count()

    if request.method == 'POST':
        if employees_count > 0:
            messages.error(request, f'لا يمكن حذف الدور {role.name} لأنه مرتبط بـ {employees_count} موظف')
            return redirect('role_detail', pk=role.pk)

        role_name = role.name
        role.delete()
        messages.success(request, f'تم حذف الدور {role_name} بنجاح')
        return redirect('role_list')

    context = {
        'role': role,
        'employees_count': employees_count,
    }
    return render(request, 'inventory/role_confirm_delete.html', context)


import openpyxl
from django.http import HttpResponse


@login_required
def export_reports_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "تقرير المبيعات"

    ws.append(["المنتج", "الكمية المباعة", "إجمالي الإيرادات"])

    top_products = SaleInvoiceItem.objects.values("product__name").annotate(
        total_quantity=Sum("quantity"),
        total_revenue=Sum("total_price")
    ).order_by("-total_quantity")

    for item in top_products:
        ws.append([
            item["product__name"],
            item["total_quantity"],
            float(item["total_revenue"])
        ])

    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=top_sales_report.xlsx"
    wb.save(response)
    return response


from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import FileResponse


@login_required
def export_reports_pdf(request):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica", 12)
    y = 800

    p.drawString(100, y, "تقرير المبيعات الأكثر مبيعًا")
    y -= 30
    p.drawString(100, y, "المنتج - الكمية - الإيراد")
    y -= 20

    products = SaleInvoiceItem.objects.values("product__name").annotate(
        total_quantity=Sum("quantity"),
        total_revenue=Sum("total_price")
    ).order_by("-total_quantity")

    for item in products:
        y -= 20
        line = f"{item['product__name']} - {item['total_quantity']} - {item['total_revenue']:.2f} ر.س"
        p.drawString(100, y, line)
        if y < 100:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="sales_report.pdf")
