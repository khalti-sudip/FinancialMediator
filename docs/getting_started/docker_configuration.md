# Docker Configuration Guide

This guide provides detailed information about the Docker configuration for FinancialMediator.

## Dockerfile Overview

FinancialMediator uses multiple Docker configurations tailored for different environments:

### 1. Development Dockerfile (`Dockerfile.dev`)

#### Features
- Uses Django's development server
- Hot reloading enabled
- Debug mode enabled
- Volume mounted for code changes
- Includes development tools

#### Usage
```bash
docker build -t financialmediator-dev -f Dockerfile.dev .
docker run -p 8000:8000 financialmediator-dev
```

### 2. Production Dockerfile (`Dockerfile`)

#### Features
- Uses uWSGI for production serving
- Multi-stage build for smaller image size
- Security best practices implemented
- Proper logging configuration
- Optimized resource usage

#### Configuration
The production Dockerfile includes:
- Multi-stage build for optimized image size
- Security scanning with trivy
- Proper environment variable handling
- Optimized Python package installation
- Production-ready logging setup

#### Usage
```bash
docker build -t financialmediator-prod .
docker run -p 8000:8000 financialmediator-prod
```

### 3. Production Docker Configuration (`ops/docker/Dockerfile`)

#### Features
- Optimized for production deployment
- Includes monitoring tools
- Proper resource limits
- Health check endpoints
- Production security settings

#### Configuration
The production Docker configuration includes:
- Resource limits and constraints
- Health check endpoints
- Monitoring tools
- Security best practices
- Production logging setup

#### Usage
```bash
docker build -t financialmediator-prod-ops -f ops/docker/Dockerfile .
docker run -p 8000:8000 financialmediator-prod-ops
```

## Docker Compose Configuration

The project includes a `docker-compose.yml` file for managing multiple services:

### Services

1. **Web Application**
   - Main Django application
   - Uses production Dockerfile
   - Configured for high availability

2. **Database**
   - PostgreSQL 15
   - Persistent storage
   - Backup configuration

3. **Redis**
   - Caching and queueing
   - Persistent storage
   - Resource limits

4. **Celery Worker**
   - Background task processing
   - Resource limits
   - Monitoring endpoints

### Environment Variables

The Docker Compose configuration uses environment variables from `.env`:

```env
# Core Settings
DJANGO_SETTINGS_MODULE=core.settings
DJANGO_SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/financialmediator

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

## Building and Running

### Build All Services

```bash
docker-compose build
```

### Run All Services

```bash
docker-compose up
```

### Run in Detached Mode

```bash
docker-compose up -d
```

### Stop All Services

```bash
docker-compose down
```

## Monitoring and Logging

### Access Logs

```bash
docker-compose logs web
```

### Follow Logs

```bash
docker-compose logs -f web
```

### Health Checks

The application includes health check endpoints:

- `/health/` - General health check
- `/health/db/` - Database health
- `/health/redis/` - Redis health
- `/health/celery/` - Celery worker health

## Troubleshooting

### Common Issues

1. **Service Connection Errors**
   - Ensure all services are running
   - Verify network configuration
   - Check service logs

2. **Resource Limit Issues**
   - Check Docker resource limits
   - Monitor system resources
   - Adjust configuration as needed

3. **Build Issues**
   - Clear Docker cache
   - Rebuild with --no-cache
   - Verify base images

### Error Messages

If you encounter any specific error messages, please:

1. Check the logs
2. Search existing issues
3. Open a new issue with the error details
4. Include your configuration and environment details

## Best Practices

1. **Security**
   - Use secure environment variables
   - Implement proper resource limits
   - Regular security scans
   - Monitor for vulnerabilities

2. **Performance**
   - Optimize resource usage
   - Implement proper caching
   - Monitor performance metrics
   - Regular maintenance

3. **Maintenance**
   - Regular updates
   - Backup configurations
   - Monitor logs
   - Regular security audits
