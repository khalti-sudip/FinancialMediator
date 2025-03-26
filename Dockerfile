# syntax=docker/dockerfile:1

# Base image with Python 3.11
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Builder stage
FROM base as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install -r requirements.txt

# Production stage
FROM base as final

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app/

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Create a non-root user
RUN useradd -m appuser
USER appuser

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]