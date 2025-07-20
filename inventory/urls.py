from django.urls import path
from . import views

urlpatterns = [
    # لوحة التحكم
    path("", views.dashboard, name="dashboard"),
    path("employee-dashboard/", views.employee_dashboard, name="employee_dashboard"),
    
    # المنتجات
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.product_edit, name="product_edit"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),
    path("products/barcodes/", views.product_barcodes, name="product_barcodes"),
    
    # الموردين
    path("suppliers/", views.supplier_list, name="supplier_list"),
    path("suppliers/create/", views.supplier_create, name="supplier_create"),
    path("suppliers/<int:pk>/edit/", views.supplier_edit, name="supplier_edit"),
    path("suppliers/<int:pk>/delete/", views.supplier_delete, name="supplier_delete"),
    
    # العملاء
    path("customers/", views.customer_list, name="customer_list"),
    path("customers/create/", views.customer_create, name="customer_create"),
    path("customers/<int:pk>/edit/", views.customer_edit, name="customer_edit"),
    path("customers/<int:pk>/delete/", views.customer_delete, name="customer_delete"),
    
    # فواتير البيع
    path("sales/", views.sale_invoice_list, name="sale_invoice_list"),
    path("sales/create/", views.sale_invoice_create, name="sale_invoice_create"),
    path("sales/<int:pk>/", views.sale_invoice_detail, name="sale_invoice_detail"),
    path("sales/<int:pk>/delete/", views.sale_invoice_delete, name="sale_invoice_delete"),
    path("sales/<int:pk>/print/", views.sale_invoice_print, name="sale_invoice_print"),
    
    # فواتير الشراء
    path("purchases/", views.purchase_invoice_list, name="purchase_invoice_list"),
    path("purchases/create/", views.purchase_invoice_create, name="purchase_invoice_create"),
    path("purchases/<int:pk>/", views.purchase_invoice_detail, name="purchase_invoice_detail"),
    path("purchases/<int:pk>/delete/", views.purchase_invoice_delete, name="purchase_invoice_delete"),
    path("purchases/<int:pk>/print/", views.purchase_invoice_print, name="purchase_invoice_print"),
    
    # الطلبات
    path("orders/", views.order_list, name="order_list"),
    path("orders/create/", views.order_create, name="order_create"),
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/edit/", views.order_edit, name="order_edit"),
    path("orders/<int:pk>/delete/", views.order_delete, name="order_delete"),
    path("orders/<int:order_pk>/items/add/", views.order_item_create, name="order_item_create"),
    path("orders/<int:order_pk>/items/<int:pk>/edit/", views.order_item_edit, name="order_item_edit"),
    path("orders/<int:order_pk>/items/<int:pk>/delete/", views.order_item_delete, name="order_item_delete"),
    
    # التقارير
    path("reports/", views.reports, name="reports"),
    path("reports/export/excel/", views.export_reports_excel, name="export_reports_excel"),
    path("reports/export/pdf/", views.export_reports_pdf, name="export_reports_pdf"),

    # إدارة الموظفين (للمدير والأدمن فقط)
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/", views.employee_detail, name="employee_detail"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("employees/<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    # إدارة الأدوار (للمدير والأدمن فقط)
    path("roles/", views.role_list, name="role_list"),
    path("roles/create/", views.role_create, name="role_create"),
    path("roles/<int:pk>/", views.role_detail, name="role_detail"),
    path("roles/<int:pk>/edit/", views.role_edit, name="role_edit"),
    path("roles/<int:pk>/delete/", views.role_delete, name="role_delete"),

    # المرتجعات
    # مرتجعات المبيعات
    path("sale-returns/", views.sale_return_list, name="sale_return_list"),
    path("sale-returns/<int:pk>/", views.sale_return_detail, name="sale_return_detail"),
    path("sales/<int:invoice_id>/return/", views.sale_return_create, name="sale_return_create"),

    # مرتجعات المشتريات
    path("purchase-returns/", views.purchase_return_list, name="purchase_return_list"),
    path("purchase-returns/<int:pk>/", views.purchase_return_detail, name="purchase_return_detail"),
    path("purchases/<int:invoice_id>/return/", views.purchase_return_create, name="purchase_return_create"),

    # الإيرادات
    path("revenues/", views.revenue_list, name="revenue_list"),
    path("revenues/create/", views.revenue_create, name="revenue_create"),
    path("revenues/<int:pk>/", views.revenue_detail, name="revenue_detail"),
    path("revenues/<int:pk>/edit/", views.revenue_edit, name="revenue_edit"),
    path("revenues/<int:pk>/delete/", views.revenue_delete, name="revenue_delete"),

    # المصروفات
    path("expenses/", views.expense_list, name="expense_list"),
    path("expenses/create/", views.expense_create, name="expense_create"),
    path("expenses/<int:pk>/", views.expense_detail, name="expense_detail"),
    path("expenses/<int:pk>/edit/", views.expense_edit, name="expense_edit"),
    path("expenses/<int:pk>/delete/", views.expense_delete, name="expense_delete"),

    # فئات الإيرادات والمصروفات
    path("revenue-categories/", views.revenue_category_list, name="revenue_category_list"),
    path("revenue-categories/create/", views.revenue_category_create, name="revenue_category_create"),
    path("expense-categories/", views.expense_category_list, name="expense_category_list"),
    path("expense-categories/create/", views.expense_category_create, name="expense_category_create"),

    # API endpoints
    path("api/product/<int:product_id>/price/", views.get_product_price, name="get_product_price"),
    path("api/product/<int:product_id>/check/<int:quantity>/", views.check_product_availability, name="check_product_availability"),

    # WooCommerce Integration
    path("woocommerce/sync/", views.woocommerce_sync, name="woocommerce_sync"),
    
    # Shipping Integration
    path("shipping/dashboard/", views.shipping_dashboard, name="shipping_dashboard"),
    path("shipping/track/<str:tracking_number>/", views.track_shipment, name="track_shipment"),
]


