# Financial Mediator

A modern financial transaction management system with separate frontend and backend components.

## Project Structure

```
FinancialMediator/
├── backend/          # Django backend API
│   ├── api/         # REST API implementation
│   ├── core/        # Core application settings
│   ├── providers/   # Payment provider integrations
│   └── banking/     # Banking-related functionality
├── frontend/        # React frontend application
│   ├── src/        # Source code
│   ├── public/     # Static files
│   └── tests/      # Test files
└── docs/           # Documentation
```

## Features

### Backend
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

### Frontend
- **Modern UI**: Built with React and Material-UI
- **State Management**: Redux Toolkit for global state management
- **Routing**: React Router for navigation
- **Form Handling**: Formik + Yup for form validation
- **Data Visualization**: Chart.js for transaction analytics
- **Responsive Design**: Mobile-first approach
- **API Integration**: Type-safe API calls with TypeScript
- **Authentication**: Secure authentication flows
- **Real-time Updates**: WebSocket integration for live updates

## Tech Stack

### Backend
- **Framework**: Django 5.0 with Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **Documentation**: drf-spectacular
- **Monitoring**: Prometheus, Sentry
- **Testing**: pytest with comprehensive test coverage

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **UI Components**: Material-UI
- **State Management**: Redux Toolkit
- **Routing**: React Router
- **Form Handling**: Formik + Yup
- **Charts**: Chart.js
- **WebSocket**: Real-time updates

## Prerequisites

### Backend
- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### Frontend
- Node.js 16+
- npm or yarn

## Installation

### Backend

1. Clone the repository:
```bash
git clone https://github.com/khalti-sudip/FinancialMediator.git
cd FinancialMediator/backend
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

### Frontend

1. Navigate to the frontend directory:
```bash
cd FinancialMediator/frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Create a .env file:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

## Running the Application

### Using Docker

1. Build and run both services using Docker Compose:
```bash
docker-compose -f backend/docker-compose.yml -f frontend/docker-compose.yml up --build
```

2. The services will be available at:
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/api/docs/
- Health Check: http://localhost:8000/api/health/

### Local Development

1. Start the backend server:
```bash
cd backend
python manage.py runserver
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Start Celery worker:
```bash
cd backend
celery -A backend worker --loglevel=info
```

4. Start Celery beat:
```bash
cd backend
celery -A backend beat --loglevel=info
```

## Environment Variables

### Backend
```env
# Core
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_NAME=financial_mediator
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# JWT
JWT_SECRET_KEY=your-jwt-secret
```

### Frontend
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_VERSION=v1
```

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

### Backend

Run backend tests:
```bash
cd backend
python -m pytest
```

### Frontend

Run frontend tests:
```bash
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
