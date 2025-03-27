# FinancialMediator Operations

This directory contains all the operations-related code and configuration files for the FinancialMediator project.

## Directory Structure

- `docker/`: Docker-related files and configurations
- `scripts/`: Helper scripts for deployment and maintenance
- `templates/`: Configuration templates
- `k8s/`: Kubernetes deployment manifests

## Prerequisites

- Docker
- Docker Compose
- Minikube
- kubectl
- Python 3.11+

## Local Development Setup

1. Create a copy of `.env.example` as `.env` and update the values
2. Run the setup script:
   ```bash
   ./ops/scripts/setup-dev-env.sh
   ```

## Docker Development

To build and run the application using Docker:

```bash
# Build the Docker image
docker build -t financial-mediator:latest -f ops/docker/Dockerfile .

# Run the container
docker run -p 8000:8000 -v $(pwd):/app -e DJANGO_SETTINGS_MODULE=core.settings financial-mediator:latest
```

## Kubernetes Deployment

1. Start Minikube:
   ```bash
   minikube start --memory=4096 --cpus=2
   ```

2. Deploy the application:
   ```bash
   ./ops/scripts/deploy-k8s.sh
   ```

3. Access the application:
   ```bash
   minikube service financialmediator --namespace=financial-mediator
   ```

## Monitoring and Logging

The application uses OpenTelemetry for monitoring. Traces and metrics can be accessed through the OpenTelemetry Collector UI.

## Health Checks

The application provides health check endpoints:
- `/health/` - General health status
- `/health/db/` - Database health
- `/health/cache/` - Cache health
- `/health/celery/` - Celery worker health
