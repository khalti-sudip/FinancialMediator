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
- Modular architecture for multiple financial institutions and providers
- Independent KYC service for verification

## Modular Architecture

FinancialMediator is designed as a modular system with clear separation between:

1. **Financial Institutions**
   - Banks
   - Digital Wallets
   - Other financial service providers
   - Each institution can send requests to multiple providers

2. **Financial Providers**
   - Payment Gateways
   - KYC Services
   - Bank Integration Services
   - Digital Wallet Services
   - Each provider can handle requests from multiple institutions

3. **KYC Service**
   - Independent verification service
   - Supports multiple verification types:
     - Document verification
     - Face verification
     - Address verification
     - Background check
   - Provider-specific verification requirements
   - Status tracking and reporting

4. **Core Components**
   - Provider Registry
   - Request Routing
   - Response Processing
   - Health Monitoring
   - Rate Limiting

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

## Adding New Providers

To add a new provider:

1. Create a new provider class that inherits from `BaseProvider`
2. Implement all required abstract methods
3. Register the provider in the registry

Example:
```python
from providers.base.provider import BaseProvider
from providers.utils.registry import registry

class MyProvider(BaseProvider):
    def initialize(self, config):
        # Implementation
        pass
    
    def authenticate(self):
        # Implementation
        pass
    
    # Implement other required methods

# Register the provider
registry.register_provider('my_provider', MyProvider)
```

## Adding New Financial Institutions

To add a new financial institution:

1. Create a new institution class that inherits from `BaseFinancialInstitution`
2. Implement all required abstract methods
3. Register the institution in the registry

Example:
```python
from providers.base.provider import BaseFinancialInstitution
from providers.utils.registry import registry

class MyInstitution(BaseFinancialInstitution):
    def get_institution_id(self):
        # Implementation
        pass
    
    def validate_credentials(self):
        # Implementation
        pass
    
    # Implement other required methods

# Register the institution
registry.register_institution('my_institution', MyInstitution)
```

## Adding New KYC Providers

To add a new KYC provider:

1. Create a new provider class that inherits from `BaseKYCProvider`
2. Create a client class that inherits from `BaseKYCClient`
3. Register both in the KYC registry

Example:
```python
from services.kyc.providers.base import BaseKYCProvider, BaseKYCClient
from services.kyc.utils.registry import kyc_registry

class MyKYCProvider(BaseKYCProvider):
    def initialize(self, config):
        # Implementation
        pass
    
    def authenticate(self):
        # Implementation
        pass
    
    # Implement other required methods

# Register the provider
kyc_registry.register_provider('my_kyc', MyKYCProvider)
```

## Project Structure

```
.
├── banking_api/           # Main API implementation
├── banking_project/      # Django project settings
├── core/                 # Core utilities and helpers
├── k8s/                 # Kubernetes configuration
├── providers/           # Provider integration system
│   ├── base/           # Base provider interfaces
│   ├── financial_institutions/  # Financial institution implementations
│   ├── financial_providers/    # Financial provider implementations
│   └── utils/          # Utility functions
├── services/           # Independent services
│   └── kyc/           # KYC verification service
│       ├── models/    # KYC models
│       ├── providers/ # KYC provider implementations
│       └── utils/     # KYC utility functions
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
- KYC-specific security controls

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.