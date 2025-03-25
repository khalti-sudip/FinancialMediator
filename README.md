# Financial Mediator API

A Django REST Framework-based API that mediates financial transactions between various payment providers and banking systems.

## Features

- **Provider Integration**: Seamless integration with multiple financial service providers
- **Transaction Management**: Handle various types of financial transactions
- **Authentication & Security**: JWT-based authentication and robust security measures
- **Caching & Performance**: Redis-based caching for optimal performance
- **Task Queue**: Celery-based background task processing
- **Monitoring**: Prometheus metrics and Sentry error tracking
- **API Documentation**: OpenAPI/Swagger documentation
- **WebSocket Support**: Real-time transaction updates

## Tech Stack

- **Framework**: Django 5.0 with Django REST Framework
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery with Redis broker
- **Documentation**: drf-spectacular
- **Monitoring**: Prometheus, Sentry
- **Testing**: pytest

## Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/financial-mediator.git
cd financial-mediator
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

## API Documentation

- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

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
financial-mediator/
├── api/                    # Core API functionality
├── banking/               # Banking integration
├── core/                  # Project configuration
├── providers/             # Provider integration
├── templates/             # HTML templates
├── static/               # Static files
├── tests/                # Test suite
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
