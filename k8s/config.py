"""
Configuration for Kubernetes deployment.
"""

from typing import Dict, Any

# Application configuration
APP_NAME = "financialmediator"
NAMESPACE = "financialmediator"
REPLICAS = 1

# Environment variables
ENV_VARS = {
    "DEBUG": "1",
    "DATABASE_URL": "postgresql://postgres:postgres@db:5432/financialmediator",
    "SECRET_KEY": "django-insecure-5e8a7b9c1d2e3f4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z4",
    "ALLOWED_HOSTS": "localhost,127.0.0.1",
    "DJANGO_SETTINGS_MODULE": "core.settings.local"
}

# PostgreSQL configuration
POSTGRES_CONFIG = {
    "db": "financialmediator",
    "user": "postgres",
    "password": "postgres",
    "storage": "1Gi"
}

# Volume configuration
VOLUME_CONFIG = {
    "host_path": "/c/Users/Dell/FinancialMediator",
    "postgres_path": "/c/Users/Dell/FinancialMediator/data/postgres"
}

# Service configuration
SERVICE_CONFIG = {
    "port": 8000,
    "target_port": 8000,
    "type": "NodePort"
}

# Image configuration
IMAGE_CONFIG = {
    "web": "python:3.11-slim",
    "postgres": "postgres:15"
}
