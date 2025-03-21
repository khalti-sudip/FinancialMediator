
# Banking Middleware API

A Django-based middleware application for managing banking operations, KYC, and investment accounts integration.

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

## Technical Setup

1. Install project dependencies:
```bash
python manage.py collectstatic
```

2. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

3. Start the server:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 banking_project.wsgi:application
```

## API Documentation

The API follows REST architecture with these main endpoints:

- `/api/auth/` - Authentication endpoints
- `/api/kyc/` - KYC profile management
- `/api/transactions/` - Transaction processing
- `/api/system-config/` - System configuration
- `/api/audit-logs/` - Audit trail access

## Models

- `User` - Custom user model for authentication
- `KYCProfile` - Customer KYC information
- `DematAccount` - Demat account details
- `Transaction` - Transaction tracking
- `SystemConfig` - Provider configuration
- `ApiKey` - API authentication
- `AuditLog` - System audit trail
- `Portfolio` - Investment portfolio tracking

## Development

The project uses:
- Django for the web framework
- Django REST Framework for API
- JWT for authentication
- PostgreSQL for database
- Gunicorn for deployment

## Security

- ISO 27001 compliant architecture
- Secure API key management
- Comprehensive audit logging
- Role-based access control
- Request validation and sanitization
