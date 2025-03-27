# FinancialMediator

A scalable, microservices-based financial management platform built with Django, designed for high availability, rate limiting, and comprehensive monitoring.

## Overview

FinancialMediator is a robust financial services middleware platform that acts as a bridge between financial institutions, payment gateways, and banking systems. It provides a unified API interface for various financial operations while handling complex integration, rate limiting, and monitoring requirements.

## Core Features

### Financial Operations

1. **Transaction Processing**
   - Real-time transaction processing
   - Multi-currency support
   - Transaction validation and verification
   - Audit logging for all operations

2. **Provider Integration**
   - Modular provider system
   - Support for multiple financial institutions
   - Dynamic configuration management
   - Provider-specific rate limiting

3. **KYC Management**
   - Comprehensive KYC verification
   - Document validation
   - Face verification integration
   - Compliance tracking

### Security & Compliance

1. **Rate Limiting**
   - Global rate limiting using Redis
   - Per-user rate limiting
   - View-specific rate limiting
   - Request bucketing for high traffic

2. **Authentication & Authorization**
   - JWT-based authentication
   - Role-based access control
   - API key management
   - Secure session handling

3. **Data Protection**
   - End-to-end encryption
   - Secure storage of sensitive data
   - Audit logging of all operations
   - Compliance with financial regulations

### Monitoring & Observability

1. **Health Monitoring**
   - Real-time system health checks
   - Database connectivity monitoring
   - Cache performance tracking
   - Celery worker status monitoring

2. **Performance Metrics**
   - Request response time tracking
   - Database query optimization
   - Cache hit/miss ratios
   - Resource utilization monitoring

3. **Logging & Tracing**
   - Distributed tracing with OpenTelemetry
   - Comprehensive logging system
   - Error tracking and reporting
   - Performance profiling

## Technical Architecture

### Core Components

1. **API Gateway**
   - Rate limiting middleware
   - Authentication handling
   - Request routing
   - Response transformation

2. **Service Layer**
   - Transaction processing
   - Provider integration
   - KYC verification
   - Health monitoring

3. **Data Layer**
   - PostgreSQL for primary storage
   - Redis for caching and queueing
   - Connection pooling for performance

4. **Infrastructure**
   - Docker containerization
   - Kubernetes orchestration
   - OpenTelemetry for monitoring
   - CI/CD pipeline integration

## Environment and Configuration Management

### Environment Variables

The application uses `django-environ` for environment variable management. All sensitive configurations should be stored in environment variables.

#### Required Environment Variables

```bash
# Core Django
SECRET_KEY=your-secret-key
DEBUG=0
ALLOWED_HOSTS=your-hosts

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Redis
REDIS_URL=redis://user:password@host:port/db

# Celery
CELERY_BROKER_URL=redis://user:password@host:port/db
CELERY_RESULT_BACKEND=redis://user:password@host:port/db

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_EXPIRE_MINUTES=30
JWT_REFRESH_DAYS=7

# OpenTelemetry
OTEL_SERVICE_NAME=financialmediator
OTEL_EXPORTER_OTLP_ENDPOINT=your-otlp-endpoint
OTEL_EXPORTER_OTLP_INSECURE=true

# Security
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

### Configuration Files

The application uses separate configuration files for different environments:

- `financialmediator/settings/base.py`: Base settings common to all environments
- `financialmediator/settings/development.py`: Development-specific settings
- `financialmediator/settings/production.py`: Production-specific settings

### Environment-Specific Settings

#### Development

- Debug mode enabled
- Local database and Redis configurations
- Console email backend
- Debug toolbar enabled
- CORS allowed for development

#### Production

- Debug mode disabled
- Secure SSL/TLS settings
- Production database and Redis configurations
- SMTP email backend
- Strict CORS settings
- Enhanced security headers

## Docker and Kubernetes Deployment

### Docker Build

The application uses a multi-stage Docker build for optimization:

```bash
docker build -t financialmediator:latest .
```

### Kubernetes Deployment

The Kubernetes deployment includes:

1. **Application Deployment**
   - 3 replicas for high availability
   - Resource limits and requests
   - Health checks (liveness, readiness, startup)
   - Volume mounts for logs
   - Environment configuration via ConfigMap and Secret

2. **Configuration Management**
   - ConfigMap for non-sensitive settings
   - Secret for sensitive values
   - Environment-specific configurations

3. **Monitoring and Logging**
   - OpenTelemetry integration
   - ServiceMonitor for Prometheus
   - Structured logging
   - Health check endpoints

### Kubernetes Manifests

The following Kubernetes manifests are available:

- `k8s/deployments/app-deployment.yaml`: Application deployment
- `k8s/configmaps/app-config.yaml`: Configuration settings
- `k8s/secrets/app-secrets.yaml`: Sensitive values
- `k8s/monitoring/service-monitor.yaml`: Monitoring configuration

### Deployment Process

```bash
# Create namespace
kubectl create namespace financialmediator

# Deploy secrets
kubectl apply -f k8s/secrets/app-secrets.yaml

# Deploy configmap
kubectl apply -f k8s/configmaps/app-config.yaml

# Deploy application
kubectl apply -f k8s/deployments/app-deployment.yaml

# Deploy monitoring
kubectl apply -f k8s/monitoring/service-monitor.yaml
```

### Health Checks

The application includes three types of health checks:

1. **Liveness Probe**
   - Checks if the application is running
   - Path: `/health/`
   - Initial delay: 30s
   - Period: 10s
   - Timeout: 5s

2. **Readiness Probe**
   - Checks if the application is ready to serve traffic
   - Path: `/health/`
   - Initial delay: 5s
   - Period: 10s
   - Timeout: 5s

3. **Startup Probe**
   - Checks if the application has started successfully
   - Path: `/health/`
   - Initial delay: 0s
   - Period: 10s
   - Timeout: 10s

### Monitoring

The application uses OpenTelemetry for monitoring:

- Distributed tracing
- Metrics collection
- Log correlation
- Performance monitoring

The ServiceMonitor is configured to:
- Scrape metrics every 30 seconds
- Check health endpoints
- Use HTTP scheme
- Include proper timeouts

### Logging

The application uses structured logging with:

- JSON format
- Contextual information
- Correlation IDs
- Severity levels
- Request/response tracking

### Security

The deployment includes several security measures:

1. **Environment Variables**
   - Sensitive values in Secrets
   - ConfigMap for non-sensitive settings
   - Proper permissions

2. **Network Security**
   - SSL/TLS enabled
   - Secure cookies
   - CSRF protection
   - CORS configuration

3. **Resource Limits**
   - CPU and memory limits
   - Request quotas
   - Rate limiting

4. **Health Monitoring**
   - Regular health checks
   - Automatic recovery
   - Performance monitoring

## Getting Started

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis 6.0 or higher
- Docker and Docker Compose
- Node.js (for frontend development)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FinancialMediator.git
   cd FinancialMediator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Initialize the database:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

### Running the Application

#### Development

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Access the application at `http://localhost:8000`

3. Access the admin interface at `http://localhost:8000/admin`

#### Production

1. Build and run Docker containers:
   ```bash
   docker-compose up --build
   ```

2. Access the application at `http://localhost:8000`

3. Access the admin interface at `http://localhost:8000/admin`

### Docker Configuration

The project uses Docker for both development and production environments. The following Docker configurations are available:

1. **Development Dockerfile** (`Dockerfile.dev`):
   - Uses Django's development server
   - Hot reloading enabled
   - Debug mode enabled
   - Volume mounted for code changes

2. **Production Dockerfile** (`Dockerfile`):
   - Uses uWSGI for production serving
   - Multi-stage build for smaller image size
   - Security best practices implemented
   - Proper logging configuration

3. **Production Docker Configuration** (`ops/docker/Dockerfile`):
   - Optimized for production deployment
   - Includes monitoring tools
   - Proper resource limits
   - Health check endpoints

### Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and modify the following variables:

```env
# Core Settings
DJANGO_SETTINGS_MODULE=core.settings
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/financialmediator

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# Security
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Monitoring
OPENTELEMETRY_ENABLED=True
OPENTELEMETRY_ENDPOINT=your-opentelemetry-endpoint

# Rate Limiting
RATE_LIMIT_WINDOW=60
RATE_LIMIT_COUNT=100

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

## Security and Performance Monitoring

### Security Best Practices

1. **Environment Variables**
   - All sensitive configurations must be stored in environment variables
   - Never commit sensitive values to version control
   - Use `.env` files for local development only
   - Production secrets should be managed through a secrets management system

2. **Security Audits**
   - Run regular security audits using the provided `security_audit.py` script
   - Check for hardcoded secrets, missing environment variables, and SAST vulnerabilities
   - Monitor rate limiting and authentication configurations

3. **Rate Limiting**
   - Global rate limiting is configured in `settings.py`
   - View-specific rate limiting can be applied using the `@rate_limit` decorator
   - Monitor rate limiting effectiveness using the performance monitoring tools

### Performance Monitoring

1. **OpenTelemetry Integration**
   - The application uses OpenTelemetry for distributed tracing and metrics
   - All major components (Django, Redis, Requests) are instrumented
   - Performance metrics are collected and exported to an OTLP endpoint

2. **Performance Monitoring Tools**
   - Use the `performance_monitor.py` script to track:
     - Transaction processing times
     - API response times
     - Database query performance
     - Cache hit/miss ratios
     - Potential bottlenecks

3. **Profiling and Optimization**
   - Use the performance monitoring tools to identify:
     - Slow database queries
     - High cache miss rates
     - Long-running transactions
     - API endpoints with high response times
   - Optimize identified bottlenecks using:
     - Query optimization
     - Caching strategies
     - Connection pooling
     - Async operations where appropriate

### Security Audit Script Usage

```bash
python scripts/security_audit.py
```

This script will:
- Scan for hardcoded secrets
- Check environment variable configuration
- Run SAST security scans
- Verify rate limiting configuration

### Performance Monitoring Usage

```bash
python scripts/performance_monitor.py
```

This script will:
- Monitor transaction performance
- Track API response times
- Log database query performance
- Record cache hit/miss ratios
- Analyze potential bottlenecks

### Required Environment Variables

```bash
# Required for security
SECRET_KEY=your_secret_key
DATABASE_PASSWORD=your_db_password
JWT_SECRET_KEY=your_jwt_secret
REDIS_PASSWORD=your_redis_password

# Required for performance monitoring
OTEL_EXPORTER_OTLP_ENDPOINT=http://your-otlp-endpoint:4317
OTEL_SERVICE_NAME=financialmediator
```

### Security Tips

1. **Regular Audits**
   - Run security audits before each deployment
   - Review audit logs regularly
   - Keep dependencies up to date

2. **Access Control**
   - Implement proper authentication and authorization
   - Use role-based access control
   - Regularly review access permissions

3. **Data Protection**
   - Encrypt sensitive data
   - Use secure password hashing
   - Implement proper session management

### Performance Optimization Tips

1. **Database Optimization**
   - Use appropriate indexes
   - Optimize query patterns
   - Implement connection pooling
   - Use bulk operations where possible

2. **Caching Strategy**
   - Implement proper caching layers
   - Use appropriate cache invalidation
   - Monitor cache hit rates
   - Implement cache warming strategies

3. **API Optimization**
   - Implement proper pagination
   - Use appropriate HTTP methods
   - Implement proper error handling
   - Use proper response formats

## Developer Documentation

### Local Development Setup

#### Using Virtual Environment (venv)
1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start development server:
```bash
python manage.py runserver
```

#### Using Docker
1. Build and start containers:
```bash
docker-compose up --build
```

2. Access the application:
- Web interface: http://localhost:8000
- Admin interface: http://localhost:8000/admin
- API documentation: http://localhost:8000/api/docs

### Common Development Workflows

#### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test app_name

# Run specific test file
python manage.py test app_name/tests/test_file.py

# Run specific test case
python manage.py test app_name.tests.test_file.TestCaseName
```

#### Running Migrations
```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Show pending migrations
python manage.py showmigrations
```

#### Creating Superuser
```bash
python manage.py createsuperuser
```

### Logging Configuration

The application uses structured logging with OpenTelemetry. Logs are formatted in JSON for easy integration with centralized logging systems.

#### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General operational information
- `WARNING`: Potential issues that don't prevent operation
- `ERROR`: Issues that prevent normal operation
- `CRITICAL`: Severe errors that require immediate attention

#### Log Format
```json
{
    "timestamp": "2025-03-27T12:00:00+05:45",
    "level": "INFO",
    "service": "financialmediator",
    "component": "api",
    "request_id": "123456789",
    "user_id": "123",
    "message": "User created successfully",
    "details": {
        "user_email": "user@example.com",
        "operation": "create_user"
    }
}
```

### Modular Django Apps

The application is organized into domain-specific Django apps:

1. `core` - Core application settings and utilities
2. `banking_api` - Banking API endpoints and services
3. `providers` - Financial provider integrations
4. `audit` - Audit logging and tracking
5. `security` - Authentication and authorization
6. `monitoring` - Health checks and performance monitoring

#### Adding New Features

1. Create a new app:
```bash
python manage.py startapp new_feature
```

2. Follow the directory structure:
```
new_feature/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── services/
│   ├── __init__.py
│   └── service_name.py
├── utils/
│   ├── __init__.py
│   └── utils.py
├── views/
│   ├── __init__.py
│   └── views.py
└── tests/
    ├── __init__.py
    └── test_views.py
```

### Troubleshooting Common Issues

#### Database Connection Issues
1. Check if PostgreSQL is running
2. Verify database credentials in `.env`
3. Run migrations: `python manage.py migrate`

#### Rate Limiting Errors
1. Check Redis connection
2. Verify rate limit configuration
3. Monitor request patterns

#### Celery Worker Issues
1. Check if Redis is running
2. Verify worker logs
3. Restart workers: `celery -A banking_project worker --loglevel=info`

#### API Errors
1. Check request logs
2. Verify API key permissions
3. Check rate limits
4. Review error responses for details

### Best Practices

1. **Code Organization**
   - Keep related functionality in the same module
   - Use clear, descriptive function names
   - Add comprehensive docstrings

2. **Testing**
   - Write unit tests for all new features
   - Use pytest fixtures for test setup
   - Maintain high test coverage

3. **Logging**
   - Include request_id in all logs
   - Add context to error messages
   - Use appropriate log levels
   - Follow JSON log format

4. **Security**
   - Validate all inputs
   - Use secure defaults
   - Follow least privilege principle
   - Regular security audits

### Deployment

#### Local Deployment
```bash
# Start Minikube
python k8s/setup_minikube.py

# Deploy application
python k8s/manager.py deploy

# Clean up
python k8s/manager.py cleanup
python k8s/cleanup_minikube.py
```

#### Production Deployment
1. Update environment variables
2. Run database migrations
3. Start services in order:
   - Database
   - Cache
   - Celery workers
   - Web application

### Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

### License

This project is licensed under the MIT License - see the LICENSE file for details.

### Support

For support, please:

1. Check the documentation
2. Search existing issues
3. Open a new issue if needed
4. Contact the maintainers

## Project Structure

```
FinancialMediator/
├── core/                # Django project settings and configurations
├── banking_api/         # Financial services API
│   ├── serializers/    # API serializers
│   ├── views/         # API views
│   └── urls/         # API URL routing
├── providers/          # Financial provider implementations
│   ├── base/         # Base provider classes
│   └── utils/        # Provider utilities
├── kyc/               # KYC verification service
│   ├── models/       # KYC models
│   ├── providers/    # KYC provider implementations
│   └── utils/       # KYC utility functions
├── ops/               # Operations and deployment
│   ├── docker/      # Docker configurations
│   ├── k8s/        # Kubernetes manifests
│   ├── scripts/    # Deployment scripts
│   └── templates/  # Configuration templates
└── tests/           # Test suite