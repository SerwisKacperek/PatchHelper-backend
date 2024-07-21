from django.apps import AppConfig

class PostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patcher'

    def ready(self):
        import patcher.signals
