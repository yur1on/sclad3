from django.apps import AppConfig

class UserRegistrationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_registration'

    def ready(self):
        import user_registration.signals  # Импортируем сигналы
