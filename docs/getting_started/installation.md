# Installation Guide

This guide provides step-by-step instructions for installing and setting up FinancialMediator.

## Prerequisites

Before installing FinancialMediator, ensure you have the following prerequisites installed:

### System Requirements

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Redis 6.0 or higher
- Docker and Docker Compose
- Node.js (for frontend development)

### Development Tools

- Git
- Virtualenv (recommended)
- Code editor or IDE

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/FinancialMediator.git
cd FinancialMediator
```

### 2. Set Up Python Environment

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Node.js dependencies (if applicable):

```bash
npm install
```

### 4. Configure Environment

Copy the example environment file and modify it with your configuration:

```bash
cp .env.example .env
```

Edit the `.env` file with your specific configuration:

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

### 5. Initialize the Database

Run database migrations:

```bash
python manage.py migrate
```

### 6. Create Superuser (Optional)

Create a superuser account for the admin interface:

```bash
python manage.py createsuperuser
```

## Running the Application

### Development Mode

Start the development server:

```bash
python manage.py runserver
```

Access the application at `http://localhost:8000`

Access the admin interface at `http://localhost:8000/admin`

### Production Mode

Build and run Docker containers:

```bash
docker-compose up --build
```

Access the application at `http://localhost:8000`

Access the admin interface at `http://localhost:8000/admin`

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.env`
   - Check database connection settings

2. **Redis Connection Error**
   - Ensure Redis is running
   - Verify Redis URL in `.env`
   - Check Redis permissions

3. **Python Virtual Environment Issues**
   - Ensure virtualenv is properly activated
   - Verify Python version matches requirements
   - Reinstall dependencies if needed

### Error Messages

If you encounter any specific error messages, please:

1. Check the logs
2. Search existing issues
3. Open a new issue with the error details
4. Include your configuration and environment details

## Next Steps

Once installed, you can:

1. Configure providers in the admin interface
2. Set up rate limiting rules
3. Configure monitoring settings
4. Start developing new features

For more detailed guides, check out our [Documentation](../README.md).
