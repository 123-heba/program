from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        # تعطيل تحميل الـ signals مؤقت
        # import inventory.signals
        pass
