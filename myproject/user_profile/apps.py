from django.apps import AppConfig

class UserProfileConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_profile'

    def ready(self):
        from django.utils.module_loading import autodiscover_modules
        autodiscover_modules('user_signals')

