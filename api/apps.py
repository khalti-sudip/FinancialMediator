from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """
        Run code when Django starts.
        """
        # Import signal handlers to register them
        try:
            import api.signals  # noqa
        except ImportError:
            pass
