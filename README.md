# Financial Mediator API

A Django REST Framework-based API that mediates financial transactions between various payment providers and banking systems.

## Features

- **Multi-Provider Integration**: Seamless integration with multiple payment providers, wallet services, banking systems, and KYC verification services
- **Transaction Management**: Comprehensive handling of deposits, withdrawals, payments, refunds, and transfers
- **Payment Method Management**: Support for adding, verifying, and managing various payment methods
- **Webhook Processing**: Automated handling of provider webhooks with retry logic and signature verification
- **Authentication & Security**: JWT-based authentication with robust request validation and error handling
- **Caching & Performance**: Redis-based caching for optimal performance and reduced API calls
- **Task Queue**: Celery-based background task processing for asynchronous operations
- **Monitoring**: Prometheus metrics, health checks, and Sentry error tracking
- **API Documentation**: Comprehensive OpenAPI/Swagger documentation with usage examples
- **WebSocket Support**: Real-time transaction updates and notifications

## Tech Stack

- **Framework**: Django 5.0 with Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **Documentation**: drf-spectacular
- **Monitoring**: Prometheus, Sentry
- **Testing**: pytest with comprehensive test coverage

## Modules

### Core
- Configuration, settings, and base functionality
- Celery setup for background tasks
- Error handling and middleware

### API
- Authentication and authorization
- Request tracking and rate limiting
- Health checks and system monitoring
- Common utilities and serializers

### Providers
- Payment provider integration (Stripe, PayPal, etc.)
- Wallet provider integration (electronic wallets)
- Banking provider integration
- KYC verification integration
- Webhook handling and signature verification
- API key management and security

### Banking
- Account management (create, verify, balance operations)
- Transaction processing (deposits, withdrawals, transfers)
- Payment processing and method management
- Statement generation and reporting

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/khalti-sudip/FinancialMediator.git
cd FinancialMediator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

## Running the Application

1. Start Redis:
```bash
redis-server
```

2. Start Celery worker:
```bash
celery -A core worker -l info
```

3. Start Celery beat (for scheduled tasks):
```bash
celery -A core beat -l info
```

4. Run the development server:
```bash
python manage.py runserver
```

## Docker Setup

1. Build and run the application using Docker Compose:
```bash
docker-compose up --build
```

2. The application will be available at:
- Web: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs/
- Health Check: http://localhost:8000/api/health/

3. Access the Django admin interface at http://localhost:8000/admin/

## Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Key environment variables:
- `DJANGO_SECRET_KEY`: Django secret key
- `DEBUG`: Development mode (True/False)
- `ALLOWED_HOSTS`: Allowed hostnames
- `DATABASE_URL`: PostgreSQL connection URL
- `REDIS_URL`: Redis connection URL
- `CELERY_BROKER_URL`: Celery broker URL
- `CELERY_RESULT_BACKEND`: Celery result backend URL
- `RATE_LIMIT_REQUESTS`: API rate limit requests
- `RATE_LIMIT_DURATION`: API rate limit duration (seconds)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

## API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

### API Endpoints

#### Providers
- `GET /api/v1/providers/` - List all providers
- `POST /api/v1/providers/` - Create a new provider
- `GET /api/v1/providers/{id}/` - Get provider details
- `POST /api/v1/providers/{id}/check_status/` - Check provider status
- `POST /api/v1/providers/{id}/update_status/` - Update provider status
- `GET /api/v1/providers/{id}/statistics/` - Get provider statistics

#### Provider Keys
- `GET /api/v1/provider-keys/` - List all API keys
- `POST /api/v1/provider-keys/` - Create a new API key
- `POST /api/v1/provider-keys/{id}/deactivate/` - Deactivate an API key
- `GET /api/v1/provider-keys/{id}/usage/` - Get API key usage

#### Provider Webhooks
- `GET /api/v1/provider-webhooks/` - List all webhooks
- `POST /api/v1/provider-webhooks/` - Create a new webhook event
- `POST /api/v1/provider-webhooks/{id}/retry/` - Retry processing a webhook
- `POST /api/v1/provider-webhooks/{id}/cancel/` - Cancel a pending webhook
- `GET /api/v1/provider-webhooks/summary/` - Get webhook processing summary

#### Banking
- `GET /api/v1/accounts/` - List all accounts
- `POST /api/v1/accounts/` - Create a new account
- `GET /api/v1/accounts/{id}/balance/` - Get account balance
- `POST /api/v1/accounts/{id}/deposit/` - Deposit funds
- `POST /api/v1/accounts/{id}/withdraw/` - Withdraw funds
- `GET /api/v1/accounts/{id}/transactions/` - Get transaction history
- `GET /api/v1/accounts/{id}/statement/` - Get account statement

#### Payments
- `GET /api/v1/payment-methods/` - List all payment methods
- `POST /api/v1/payment-methods/` - Create a new payment method
- `POST /api/v1/payment-methods/{id}/verify/` - Verify a payment method
- `POST /api/v1/payment-methods/{id}/deactivate/` - Deactivate a payment method
- `POST /api/v1/payments/process/` - Process a payment
- `POST /api/v1/payments/cancel/` - Cancel a payment
- `POST /api/v1/payments/refund/` - Refund a payment

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=.
```

## Code Quality

Format code:
```bash
black .
isort .
```

Lint code:
```bash
flake8
```

## Monitoring

- Prometheus metrics: http://localhost:8000/metrics
- Health check: http://localhost:8000/health/

## Deployment

1. Set production environment variables
2. Collect static files:
```bash
python manage.py collectstatic
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Start the application with gunicorn:
```bash
gunicorn core.wsgi:application
```

## Project Structure

```
FinancialMediator/
├── api/                  # Core API functionality
│   ├── middleware/       # Custom middleware
│   ├── views/            # API views
│   ├── models.py         # API models
│   ├── serializers.py    # API serializers
│   ├── tasks.py          # Background tasks
│   └── error_handlers.py # Error handling
├── banking/              # Banking integration
│   ├── views/            # Banking views
│   ├── models.py         # Banking models
│   ├── serializers.py    # Banking serializers
│   ├── services.py       # Banking services
│   └── tasks.py          # Banking tasks
├── core/                 # Project configuration
│   ├── settings.py       # Django settings
│   ├── urls.py           # URL routing
│   ├── celery.py         # Celery configuration
│   ├── wsgi.py           # WSGI configuration
│   └── asgi.py           # ASGI configuration
├── providers/            # Provider integration
│   ├── views/            # Provider views
│   ├── handlers/         # Webhook handlers
│   ├── models.py         # Provider models
│   ├── serializers.py    # Provider serializers
│   ├── tasks.py          # Provider tasks
│   └── utils.py          # Provider utilities
├── docs/                 # Documentation
│   ├── api/              # API docs
│   └── deployment/       # Deployment guides
├── tests/                # Test suite
│   ├── api/              # API tests
│   ├── banking/          # Banking tests
│   └── providers/        # Provider tests
├── templates/            # HTML templates
├── static/               # Static files
├── .env                  # Environment variables
├── manage.py             # Django management script
└── requirements.txt      # Project dependencies
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
