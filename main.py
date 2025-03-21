import os
import logging
import django
from django.core.wsgi import get_wsgi_application

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_project.settings')

# Configure basic logging early
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger('app')

# Initialize Django
django.setup()

# Get WSGI application for uWSGI
application = get_wsgi_application()

# Log database connection status
db_url = os.environ.get('DATABASE_URL', 'Not configured')
logger.info(f"Using database: {db_url}")

if __name__ == "__main__":
    # Log successful initialization
    logger.info("Application initialized successfully with default configuration")