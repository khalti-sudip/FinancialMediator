from django.apps import AppConfig


class BankingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banking'

    def ready(self):
        """
        Run code when Django starts.
        """
        # Import signal handlers to register them
        try:
            import banking.signals  # noqa
        except ImportError:
            pass
