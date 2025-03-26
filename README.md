# FinancialMediator

A Django-based financial management system with rate limiting, health monitoring, and containerized deployment.

## Project Overview

FinancialMediator is a Django application that provides financial management capabilities with the following features:

- Rate limiting middleware for API protection
- Comprehensive health monitoring system
- Containerized deployment with Kubernetes
- PostgreSQL database integration
- Redis for caching and Celery task queue
- REST API with Django REST Framework

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Kubernetes (tested with Minikube)
- Docker

## Local Development Setup

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and configure your environment variables.

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

The application will be available at http://localhost:8000

## Kubernetes Deployment

### Prerequisites

- Minikube
- kubectl
- Docker

### Setup Instructions

1. Start Minikube:
   ```bash
   minikube start
   ```

2. Apply the Kubernetes configuration:
   ```bash
   kubectl apply -f k8s/configmaps/app-config.yaml
   kubectl apply -f k8s/configmaps/app-files.yaml
   kubectl apply -f k8s/deployments/django-deployment.yaml
   kubectl apply -f k8s/deployments/celery-deployment.yaml
   kubectl apply -f k8s/deployments/postgres-deployment.yaml
   kubectl apply -f k8s/deployments/redis-deployment.yaml
   kubectl apply -f k8s/services/django-service.yaml
   ```

3. Verify the deployment:
   ```bash
   kubectl get pods
   kubectl get services
   ```

The application will be available at http://nabilwealth.com (configured in the service)

## Health Monitoring

The application includes a comprehensive health monitoring system that checks:
- Database connectivity
- Redis status
- Celery worker status
- Cache health

Access the health check endpoint at `/health/`

## API Documentation

The API documentation is automatically generated using drf-spectacular and is available at:
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Security Features

- Rate limiting middleware for API protection
- CORS configuration for secure cross-origin requests
- Environment-based configuration management
- Secure session and authentication handling

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.