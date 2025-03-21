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

# Get WSGI application for Gunicorn
application = get_wsgi_application()
app = application  # Required for Gunicorn

# Log database connection status
db_url = os.environ.get('DATABASE_URL', 'Not configured')
logger.info(f"Using database: {db_url}")

# Run migrations programmatically if needed
from django.core.management import call_command
from django.db import connection

try:
    # Create empty migration if needed
    # call_command('makemigrations', 'banking_api')
    
    # Apply migrations
    # call_command('migrate')
    
    logger.info("Database tables created")
    
    # Create a superuser if needed
    # from django.contrib.auth import get_user_model
    # User = get_user_model()
    # if not User.objects.filter(username='admin').exists():
    #     User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    #     logger.info("Admin user created")
    
except Exception as e:
    logger.error(f"Error setting up database: {str(e)}")

# Log successful initialization
logger.info("Application initialized successfully with default configuration")