#!/bin/sh

# Wait for PostgreSQL to be ready
wait-for-it.sh db:5432 --timeout=30 --strict -- echo "PostgreSQL is ready"

# Wait for Redis to be ready
wait-for-it.sh redis:6379 --timeout=30 --strict -- echo "Redis is ready"

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
"

# Start the application
exec "$@"
