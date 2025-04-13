from django.apps import AppConfig

class InformationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'information'

    def ready(self):
        import information.signals  # ⚠️ très important

