from django.contrib import admin
from .models import (
    Supplier, Customer, Product, PurchaseInvoice, PurchaseInvoiceItem,
    SaleInvoice, SaleInvoiceItem, Order, OrderItem,
    Employee, Role, Permission
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "created_at"]
    search_fields = ["name", "phone", "email"]
    list_filter = ["created_at"]


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["name", "phone", "email", "created_at"]
    search_fields = ["name", "phone", "email"]
    list_filter = ["created_at"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "quantity", "min_quantity", "supplier", "is_low_stock"]
    search_fields = ["name", "supplier__name"]
    list_filter = ["supplier", "created_at"]
    list_editable = ["price", "quantity", "min_quantity"]

    def is_low_stock(self, obj):
        return obj.is_low_stock

    is_low_stock.boolean = True
    is_low_stock.short_description = "مخزون منخفض"


class PurchaseInvoiceItemInline(admin.TabularInline):
    model = PurchaseInvoiceItem
    extra = 1


@admin.register(PurchaseInvoice)
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "supplier", "date", "total_amount", "created_by"]
    search_fields = ["invoice_number", "supplier__name"]
    list_filter = ["date", "supplier"]
    inlines = [PurchaseInvoiceItemInline]
    readonly_fields = ["invoice_number", "total_amount"]


class SaleInvoiceItemInline(admin.TabularInline):
    model = SaleInvoiceItem
    extra = 1


@admin.register(SaleInvoice)
class SaleInvoiceAdmin(admin.ModelAdmin):
    list_display = ["invoice_number", "customer", "date", "total_amount", "created_by"]
    search_fields = ["invoice_number", "customer__name"]
    list_filter = ["date", "customer"]
    inlines = [SaleInvoiceItemInline]
    readonly_fields = ["invoice_number", "total_amount"]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer", "order_date", "status", "total_amount", "created_by"]
    list_filter = ["status", "order_date", "customer"]
    search_fields = ["order_number", "customer__name"]
    inlines = [OrderItemInline]
    readonly_fields = ["order_number", "total_amount", "created_by", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "product", "quantity", "unit_price", "total_price"]
    search_fields = ["order__order_number", "product__name"]
    list_filter = ["order", "product"]


# ========== إدارة الموظفين والأدوار ==========

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "codename", "created_at"]
    search_fields = ["name", "codename", "description"]
    list_filter = ["created_at"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name", "is_active", "created_at"]
    search_fields = ["name", "description"]
    list_filter = ["is_active", "created_at"]
    filter_horizontal = ["permissions"]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["employee_id", "user", "role", "department", "employment_status", "hire_date"]
    search_fields = ["employee_id", "user__username", "user__first_name", "user__last_name", "department"]
    list_filter = ["employment_status", "role", "hire_date"]
    readonly_fields = ["employee_id", "created_at", "updated_at"]
    fieldsets = [
        ("معلومات المستخدم", {
            "fields": ["user"]
        }),
        ("معلومات الموظف", {
            "fields": ["employee_id", "role", "department", "phone", "address"]
        }),
        ("معلومات التوظيف", {
            "fields": ["hire_date", "salary", "employment_status", "notes"]
        }),
        ("معلومات النظام", {
            "fields": ["created_at", "updated_at"],
            "classes": ["collapse"]
        }),
    ]


