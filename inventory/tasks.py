from celery import shared_task
from .services.woocommerce_service import WooCommerceService
from .services.shipping_service import ShippingService
from .models import Order, Product
import logging

logger = logging.getLogger(__name__)

@shared_task
def sync_woocommerce_products():
    """مهمة مزامنة المنتجات من WooCommerce"""
    service = WooCommerceService()
    count = service.sync_products_from_woocommerce()
    logger.info(f"تم مزامنة {count} منتج من WooCommerce")
    return count

@shared_task
def sync_woocommerce_orders():
    """مهمة مزامنة الطلبات من WooCommerce"""
    service = WooCommerceService()
    count = service.sync_orders_from_woocommerce()
    logger.info(f"تم مزامنة {count} طلب من WooCommerce")
    return count

@shared_task
def update_woocommerce_stock(product_id, new_quantity):
    """تحديث المخزون في WooCommerce"""
    service = WooCommerceService()
    success = service.update_product_stock(product_id, new_quantity)
    if success:
        logger.info(f"تم تحديث مخزون المنتج {product_id} في WooCommerce")
    return success

@shared_task
def create_shipment_for_order(order_id):
    """إنشاء شحنة للطلب"""
    service = ShippingService()
    tracking = service.create_shipment(order_id)
    if tracking:
        logger.info(f"تم إنشاء شحنة للطلب {order_id}")
        return tracking.tracking_number
    return None

@shared_task
def update_shipping_status():
    """تحديث حالة جميع الشحنات"""
    service = ShippingService()
    count = service.update_all_shipments()
    logger.info(f"تم تحديث {count} شحنة")
    return count

@shared_task
def auto_create_shipments():
    """إنشاء شحنات تلقائية للطلبات الجديدة"""
    pending_orders = Order.objects.filter(
        status='confirmed',
        shippingtracking__isnull=True
    )
    
    created_count = 0
    for order in pending_orders:
        if create_shipment_for_order.delay(order.id):
            created_count += 1
    
    logger.info(f"تم إنشاء {created_count} شحنة تلقائية")
    return created_count