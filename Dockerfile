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
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
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
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Create log directory
RUN mkdir -p /var/log/uwsgi

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=core.settings

# Expose ports
EXPOSE 8000
EXPOSE 9191 # uWSGI stats port

# Command to run the application
CMD ["uwsgi", "--ini", "uwsgi.ini"]
