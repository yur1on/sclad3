from django.apps import AppConfig
from django.conf import settings

class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'

    def ready(self):
        # Делай сигналы опциональными. По умолчанию — ВЫКЛ.
        if getattr(settings, "WAREHOUSE_USE_TG_SIGNAL", False):
            import warehouse.signals
