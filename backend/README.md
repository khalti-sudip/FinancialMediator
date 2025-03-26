# Financial Mediator Backend

This is the backend component of the Financial Mediator API system. It provides RESTful endpoints for financial operations and integrates with various payment providers.

## Project Structure

```
backend/
├── api/              # REST API implementation
├── core/             # Core application settings and configurations
├── providers/        # Payment provider integrations
├── banking/          # Banking-related functionality
├── templates/        # Django templates
└── static/           # Static files
```

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+
- Docker (optional)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

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

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create and apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

### Using Docker

1. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```

### Local Development

1. Start the development server:
   ```bash
   python manage.py runserver
   ```

2. Start Celery worker:
   ```bash
   celery -A backend worker --loglevel=info
   ```

3. Start Celery beat:
   ```bash
   celery -A backend beat --loglevel=info
   ```

## API Documentation

The API documentation is available at `/api/docs/` when running the development server.

## Testing

Run tests using:
```bash
python -m pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
