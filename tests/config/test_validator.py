import pytest
from core.config.validator import ConfigValidator

class TestConfigValidator:
    def test_validate_config_missing_required_configs(self):
        """Test that validation fails when required configurations are missing."""
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_config()
        
        assert "Missing required configurations" in str(exc_info.value)

    def test_validate_database_config_invalid_url(self):
        """Test that database configuration validation fails with invalid URL."""
        os.environ['DATABASE_URL'] = 'invalid://url'
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_database_config()
        
        assert "DATABASE_URL must be a PostgreSQL or MySQL URL" in str(exc_info.value)

    def test_validate_cache_config_invalid_url(self):
        """Test that cache configuration validation fails with invalid URL."""
        os.environ['REDIS_URL'] = 'invalid://url'
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_cache_config()
        
        assert "REDIS_URL must be a Redis URL" in str(exc_info.value)

    def test_validate_monitoring_config_missing_service_name(self):
        """Test that monitoring configuration validation fails without service name."""
        os.environ['OTEL_SERVICE_NAME'] = ''
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_monitoring_config()
        
        assert "OTEL_SERVICE_NAME is not set" in str(exc_info.value)

    def test_validate_monitoring_config_missing_exporter_endpoint(self):
        """Test that monitoring configuration validation fails without exporter endpoint."""
        os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = ''
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_monitoring_config()
        
        assert "OTEL_EXPORTER_OTLP_ENDPOINT is not set" in str(exc_info.value)

    def test_validate_config_all_configs_present(self, monkeypatch):
        """Test that validation passes when all required configurations are present."""
        monkeypatch.setenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/dbname')
        monkeypatch.setenv('REDIS_URL', 'redis://localhost:6379')
        monkeypatch.setenv('SECRET_KEY', 'test-secret-key')
        monkeypatch.setenv('ALLOWED_HOSTS', 'localhost')
        monkeypatch.setenv('OTEL_SERVICE_NAME', 'financial-mediator')
        monkeypatch.setenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://otel-collector:4317')
        monkeypatch.setenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        monkeypatch.setenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

        try:
            ConfigValidator.validate_config()
            ConfigValidator.validate_database_config()
            ConfigValidator.validate_cache_config()
            ConfigValidator.validate_monitoring_config()
        except ImproperlyConfigured:
            pytest.fail("Validation failed with all required configurations present")

    def test_validate_config_invalid_database_url(self, monkeypatch):
        """Test that validation fails with invalid database URL."""
        monkeypatch.setenv('DATABASE_URL', 'invalid://url')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_database_config()
        
        assert "DATABASE_URL must be a PostgreSQL or MySQL URL" in str(exc_info.value)

    def test_validate_config_invalid_redis_url(self, monkeypatch):
        """Test that validation fails with invalid Redis URL."""
        monkeypatch.setenv('REDIS_URL', 'invalid://url')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_cache_config()
        
        assert "REDIS_URL must be a Redis URL" in str(exc_info.value)

    def test_validate_config_invalid_otel_service_name(self, monkeypatch):
        """Test that validation fails with invalid OpenTelemetry service name."""
        monkeypatch.setenv('OTEL_SERVICE_NAME', '')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_monitoring_config()
        
        assert "OTEL_SERVICE_NAME is not set" in str(exc_info.value)

    def test_validate_config_invalid_otel_exporter_endpoint(self, monkeypatch):
        """Test that validation fails with invalid OpenTelemetry exporter endpoint."""
        monkeypatch.setenv('OTEL_EXPORTER_OTLP_ENDPOINT', '')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_monitoring_config()
        
        assert "OTEL_EXPORTER_OTLP_ENDPOINT is not set" in str(exc_info.value)

    def test_validate_config_invalid_celery_broker_url(self, monkeypatch):
        """Test that validation fails with invalid Celery broker URL."""
        monkeypatch.setenv('CELERY_BROKER_URL', 'invalid://url')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_config()
        
        assert "Missing required configurations" in str(exc_info.value)

    def test_validate_config_invalid_celery_result_backend(self, monkeypatch):
        """Test that validation fails with invalid Celery result backend."""
        monkeypatch.setenv('CELERY_RESULT_BACKEND', 'invalid://url')
        
        with pytest.raises(ImproperlyConfigured) as exc_info:
            ConfigValidator.validate_config()
        
        assert "Missing required configurations" in str(exc_info.value)
