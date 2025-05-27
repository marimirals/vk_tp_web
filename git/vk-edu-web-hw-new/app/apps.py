
from django.apps import AppConfig

class MyAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'  # ← ВОТ ЭТО ОБЯЗАТЕЛЬНО

    def ready(self):
        import app.signals  # Убедись, что файл называется `signals.py`
