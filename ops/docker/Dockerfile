FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create log directory
RUN mkdir -p /var/log/uwsgi

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# Expose ports
EXPOSE 8000
EXPOSE 9191
from core.utils.logging import get_logger, log_info, log_error

# Get a logger
logger = get_logger(__name__)

# Log messages with structured attributes
log_info(logger, "User created", attributes={"user_id": 123, "email": "user@example.com"})

# Log errors with exceptions
try:
    # some operation
    pass
except Exception as e:
    log_error(logger, "Failed to process operation", exception=e, attributes={"operation_id": 456})
# Command to run the application
CMD ["uwsgi", "--ini", "uwsgi.ini"]
