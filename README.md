# FinancialMediator

A scalable, microservices-based financial management platform built with Django, designed for high availability, rate limiting, and comprehensive monitoring.

## Architecture Overview

### System Architecture

FinancialMediator is built as a microservices architecture with the following key components:

```
FinancialMediator
├── API Gateway
│   ├── Rate Limiter
│   ├── Authentication
│   └── Request Router
├── Core Services
│   ├── Financial Services
│   │   ├── Bank Integration
│   │   ├── Digital Wallet
│   │   └── Payment Processing
│   ├── KYC Service
│   │   ├── Document Verification
│   │   ├── Face Verification
│   │   └── Background Check
│   └── Health Monitoring
├── Data Layer
│   ├── PostgreSQL (Primary Database)
│   └── Redis (Cache & Message Queue)
└── Infrastructure
    ├── Kubernetes Cluster
    ├── OpenTelemetry Collector
    └── Celery Task Queue
```

### Key Features

1. **Microservices Architecture**
   - Independent services for financial operations, KYC, and monitoring
   - Each service can scale independently based on demand
   - Clear separation of concerns and responsibilities

2. **Security & Rate Limiting**
   - Global rate limiting middleware using Redis
   - View-specific rate limiting decorators
   - Request bucketing for high traffic scenarios
   - Security headers and authentication

3. **Monitoring & Observability**
   - OpenTelemetry integration for tracing and metrics
   - Comprehensive health check system
   - Real-time monitoring of services and infrastructure
   - Distributed tracing across microservices

4. **Scalability & Performance**
   - Async task processing with Celery
   - Redis-based caching for improved performance
   - Load balancing and auto-scaling
   - Database connection pooling

5. **Provider Integration**
   - Modular provider system for financial institutions
   - Independent KYC service for verification
   - Provider-specific configuration and requirements
   - Status tracking and reporting

## Technical Stack

### Backend
- **Framework**: Django 4.2
- **Database**: PostgreSQL 14
- **Cache**: Redis 6
- **Message Queue**: Celery with Redis
- **API**: Django REST Framework
- **Authentication**: JWT
- **Rate Limiting**: Redis-based sliding window algorithm

### Monitoring & Observability
- **Tracing**: OpenTelemetry
- **Metrics**: Prometheus
- **Logging**: ELK Stack
- **Health Checks**: Custom health monitoring system

### Infrastructure
- **Container Orchestration**: Kubernetes
- **Container Runtime**: Docker
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: Terraform
- **Secret Management**: HashiCorp Vault

## Deployment Architecture

```
Kubernetes Cluster
├── Namespaces
│   ├── financial-mediator
│   │   ├── Django Application
│   │   ├── Redis
│   │   ├── PostgreSQL
│   │   ├── Celery Workers
│   │   └── OpenTelemetry Collector
│   └── monitoring
├── Ingress Controllers
├── Load Balancers
└── Service Discovery
```

## Getting Started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Kubernetes (tested with Minikube)
- PostgreSQL 14+
- Redis 6+
- Git

### Local Development

1. Set up your environment:
   ```bash
   cd ops
   make setup-dev
   ```

2. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Kubernetes Deployment

1. Deploy to Kubernetes:
   ```bash
   cd ops
   make deploy-k8s
   ```

2. Access the application:
   ```bash
   minikube service financialmediator --namespace=financial-mediator
   ```

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
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.