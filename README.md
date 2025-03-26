# FinancialMediator

A Django-based financial management system with rate limiting, health monitoring, and Kubernetes deployment.

## Project Overview

FinancialMediator is a Django application that provides financial management capabilities with the following features:

- Rate limiting middleware for API protection
- Comprehensive health monitoring system
- Kubernetes deployment with Python-based deployment script
- PostgreSQL database integration
- Redis for caching and Celery task queue
- REST API with Django REST Framework
- Provider integration system
- Core utilities and helper functions

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 6+
- Kubernetes (tested with Minikube)
- Git

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

3. Create a `.env` file and configure your environment variables.

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
- Python 3.11+

### Setup Instructions

1. Start Minikube:
   ```bash
   minikube start
   ```

2. Run the deployment script:
   ```bash
   python scripts/deploy.py
   ```

3. Verify the deployment:
   ```bash
   kubectl get pods
   kubectl get services
   ```

The application will be available at the Kubernetes service URL

## Health Monitoring

The application includes a comprehensive health monitoring system that checks:
- Database connectivity
- Redis status
- Celery worker status
- Cache health
- Provider integration status

Access the health check endpoint at `/health/`

## API Documentation

The API documentation is automatically generated using drf-spectacular and is available at:
- Swagger UI: `/api/schema/swagger-ui/`
- ReDoc: `/api/schema/redoc/`

## Project Structure

```
.
├── banking_api/           # Main API implementation
├── banking_project/      # Django project settings
├── core/                 # Core utilities and helpers
├── k8s/                 # Kubernetes configuration
├── providers/           # External service providers
├── scripts/             # Deployment and utility scripts
├── tests/              # Test suite
├── utils/              # Utility functions
├── .env                # Environment variables
├── manage.py           # Django management script
├── pytest.ini          # Pytest configuration
├── requirements.txt    # Project dependencies
└── venv/              # Python virtual environment
```

## Security Features

- Rate limiting for API endpoints
- JWT authentication
- CORS protection
- Secure session handling
- Environment-based configuration
- Health monitoring and alerts
- Logging and error tracking
- Provider-specific security measures

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.