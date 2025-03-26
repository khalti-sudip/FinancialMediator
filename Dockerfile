# Base image with Python 3.11
FROM python:3.11-slim as base

# Build stage
FROM base as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    musl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /root/.cache

# Production stage
FROM base

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=banking_project.settings \
    GUNICORN_CMD_ARGS="--workers 3 --bind 0.0.0.0:8000 --timeout 120"

# Copy project files
COPY . /app/

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chown -R 1000:1000 /app/logs

# Set permissions
RUN chown -R 1000:1000 /app

# Switch to non-root user
USER 1000

# Collect static files
RUN python manage.py collectstatic --noinput --clear

# Command to run the application
CMD ["gunicorn", "banking_project.wsgi:application"]
