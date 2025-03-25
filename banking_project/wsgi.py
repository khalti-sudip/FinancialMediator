import os
from django.core.wsgi import get_wsgi_application
from utils.telemetry import setup_telemetry

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "banking_project.settings")

# Initialize telemetry before application
setup_telemetry()

application = get_wsgi_application()
