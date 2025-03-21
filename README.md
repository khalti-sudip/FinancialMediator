
# Banking Middleware API

A Django-based middleware application for managing banking operations, KYC, and investment accounts integration, with distributed tracing and monitoring capabilities.

## Features

### 1. Authentication & Security
- JWT-based authentication
- Role-based access control
- Audit logging
- API key management
- Request rate limiting
- Data encryption

### 2. KYC & Account Management
- Mobile number-based unique customer identification
- KYC profile creation and verification
- Demat account management
- Portfolio tracking and analytics

### 3. Transaction Management
- Multi-system transaction tracking
- Transaction status monitoring
- Error handling and retries
- Detailed transaction logging
- Response data management

### 4. System Configuration
- Dynamic provider configuration
- API authentication management
- System health monitoring
- Timeout and retry settings
- Multi-provider support

### 5. Monitoring & Observability
- Distributed tracing with OpenTelemetry
- Sampling-based trace collection
- Prometheus metrics with custom dashboards
- Enhanced logging with correlation IDs
- Real-time performance monitoring
- Resource utilization tracking

## Technical Setup

1. Install project dependencies:
```bash
python -m pip install -r requirements.txt
```

2. Setup database and static files:
```bash
python manage.py collectstatic --noinput
python manage.py migrate
```

3. Start the optimized server:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 6 --threads 2 --worker-class=gthread --worker-connections=2000 --max-requests 10000 --max-requests-jitter 1000 --keep-alive 5 --timeout 120 banking_project.wsgi:application
```

## Monitoring & Metrics

- Metrics dashboard: `/metrics_dashboard.html`
- Prometheus endpoint: `http://0.0.0.0:9090/metrics`
- Application logs: `logs/banking_middleware.log`
- Trace sampling rate: 50%
- Metric collection interval: 5 seconds

## Database Configuration

- Connection pooling enabled
- Min connections: 10
- Max connections: 50
- Connection timeout: 600s
- Keep-alive settings optimized
- Health checks enabled

## Cache Configuration

- Backend: LocMemCache
- Location: banking_middleware_cache
- Timeout: 300 seconds
- Max entries: 10000
- Cull frequency: 3

## API Documentation

RESTful endpoints:

- `/api/auth/` - Authentication
- `/api/kyc/` - KYC management
- `/api/transactions/` - Transaction processing
- `/api/system-config/` - System settings
- `/api/audit-logs/` - Audit trails

## Models

- `User` - Authentication
- `KYCProfile` - Customer KYC
- `DematAccount` - Demat accounts
- `Transaction` - Transactions
- `SystemConfig` - Configuration
- `ApiKey` - API auth
- `AuditLog` - Audit trail
- `Portfolio` - Investments

## Technology Stack

- Django & DRF
- JWT Authentication
- PostgreSQL Database
- Gunicorn Server
- OpenTelemetry
- Prometheus Metrics

## Security Features

- ISO 27001 compliance
- Secure key management
- Comprehensive auditing
- Role-based access
- Request validation
- Data sanitization
- Distributed tracing
- Real-time monitoring

## Performance Optimizations

- Connection pooling
- Request sampling
- Efficient caching
- Load balancing ready
- Distributed tracing
- Resource monitoring
- Optimized worker config
