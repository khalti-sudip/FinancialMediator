# Dockerfile for FinancialMediator
# 
# This Dockerfile defines the container image for the FinancialMediator application.
# It uses a multi-stage build process to:
# 1. Build the application and dependencies
# 2. Create a production-ready image
# 3. Copy only necessary files to the final image
# 
# Key Features:
# - Multi-stage build for smaller image size
# - Production-ready configuration with uWSGI
# - Security best practices
# - Performance optimizations

# Build stage
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install security scanning tool
RUN pip install --no-cache-dir trivy

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run security scan
RUN trivy fs /app --exit-code 1 --severity HIGH,CRITICAL

# Production stage
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create log directory
RUN mkdir -p /var/log/uwsgi

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/financialmediator /app/financialmediator
COPY --from=builder /app/manage.py /app/manage.py

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=financialmediator.settings.production

# Add health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python manage.py check --deploy --fail-level=ERROR || exit 1

# Expose ports
EXPOSE 8000
EXPOSE 9191

# Command to run the application
CMD ["gunicorn", "financialmediator.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
