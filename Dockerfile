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
FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    musl-dev \
    libpq-dev \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Install security scanning tool
RUN pip install --no-cache-dir trivy

# Copy requirements
COPY requirements.txt requirements-dev.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy application code
COPY . .

# Run security scan
RUN trivy fs /app --exit-code 1 --severity HIGH,CRITICAL

# Production stage
FROM python:3.9-slim as production

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    redis-tools \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create log directory
RUN mkdir -p /var/log/uwsgi

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /app/financialmediator /app/financialmediator
COPY --from=builder /app/manage.py /app/manage.py

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=financialmediator.settings.production

# Create non-root user
RUN useradd --create-home appuser
WORKDIR /home/appuser

# Set permissions
RUN chown -R appuser:appuser /home/appuser
USER appuser

# Expose ports
EXPOSE 8000
EXPOSE 9191

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; assert requests.get('http://localhost:8000/health/').status_code == 200"

# Command to run the application
CMD ["gunicorn", "financialmediator.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
