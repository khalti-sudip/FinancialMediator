
# Banking Middleware API

A Django-based middleware application for managing banking operations, KYC, and investment accounts integration.

## Features

### 1. Onboarding and Profile Management
- Mobile number-based unique customer identification
- eKYC profile creation and validation
- Integrated account creation for:
  - Demat Account
  - Meroshare Account
  - TMS Account
  - CASBA Account
  - PMS Account
  - SIP Account

### 2. Data Exchange and Portfolio Management
- Real-time portfolio tracking with Nepse data integration
- Portfolio performance analytics
- Profit/Loss tracking
- Automated portfolio summary reports
- Real-time price adjustments
- Portfolio sharing capabilities

### 3. Transaction Management
- Automated account renewals (Meroshare and Demat)
- SIP payment processing
- Direct bank account settlement for share purchases
- TMIS direct bank integration
- Payment link generation
- Detailed transaction narration in bank statements

### 4. API Gateway Integration
- Nepse data integration
- Payment processing APIs
- IPO application integration
- CDSC connectivity
- KYC validation APIs

### 5. Notifications
- Price adjustment alerts
- Dividend declarations
- Rights share announcements
- Merger notifications
- Trading suspension alerts
- Custom price alerts

### 6. Security Features
- JWT-based authentication
- Role-based access control
- Audit logging
- Request rate limiting
- Data encryption

## Technical Setup

1. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

2. Run migrations:
```bash
python manage.py migrate
```

3. Start the server:
```bash
gunicorn --bind 0.0.0.0:5000 --workers 3 banking_project.wsgi:application
```

## API Documentation

The API uses REST architecture with the following main endpoints:

- `/api/v1/kyc/` - KYC profile management
- `/api/v1/accounts/` - Account creation and management
- `/api/v1/portfolio/` - Portfolio tracking and analytics
- `/api/v1/transactions/` - Transaction processing
- `/api/v1/notifications/` - Alert management

## Environment Variables

Required environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `DEBUG` - Debug mode (True/False)

## Security Compliance

- ISO 27001 compliant
- PCI-DSS standards
- NRB regulatory compliance
- Implements industry-standard security measures
