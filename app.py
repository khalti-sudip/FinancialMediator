"""Flask application factory and configuration."""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_caching import Cache
from prometheus_flask_exporter import PrometheusMetrics


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""

    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
jwt = JWTManager()
migrate = Migrate()
cache = Cache()
metrics = PrometheusMetrics.for_app_factory()

# Set up basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: The configuration to use - default, development, testing, or production

    Returns:
        The configured Flask application
    """
    app = Flask(__name__)

    # Load configuration
    from config import config

    app.config.from_object(config[config_name])

    # Set database URI
    db_url = os.environ.get("DATABASE_URL", "sqlite:///financial_mediator.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url

    # Set secret key
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    metrics.init_app(app)

    # Configure security
    from api.middleware.security import configure_security

    configure_security(app)

    # Register error handlers
    from api.error_handlers import register_error_handlers

    register_error_handlers(app)

    # Configure request tracking
    from api.middleware.request_tracking import track_request_id

    track_request_id(app)

    # Configure logging within app context
    with app.app_context():
        from utils.logging_config import configure_logging

        configure_logging(app.config.get("LOG_LEVEL", "INFO"))

    # Register blueprints
    register_blueprints(app)

    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")

    # Initialize Celery
    init_celery(app)

    # Register routes
    register_routes(app)

    # Add metrics
    add_prometheus_metrics(app)

    logger.info(f"Application initialized with {config_name} configuration")
    return app


def register_blueprints(app: Flask) -> None:
    """Register Flask blueprints.

    Args:
        app: Flask application instance
    """
    # Import blueprints
    from api.health import health_bp
    from api.auth import auth_bp
    from api.providers import providers_bp
    from api.banking import banking_bp

    # Register blueprints with API versioning
    app.register_blueprint(health_bp)  # Health check endpoints don't need versioning
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(providers_bp, url_prefix="/api/v1/providers")
    app.register_blueprint(banking_bp, url_prefix="/api/v1/banking")


def init_celery(app: Flask) -> None:
    """Initialize Celery with Flask app context.

    Args:
        app: Flask application instance
    """
    from api.tasks.celery_app import celery

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    app.celery = celery


def add_prometheus_metrics(app: Flask) -> None:
    """Add custom Prometheus metrics.

    Args:
        app: Flask application instance
    """
    # Add default metrics
    metrics.info("app_info", "Application information", version="1.0.0")

    # Add custom metrics
    metrics.counter(
        "api_requests_total",
        "Total API requests",
        labels={"path": lambda: request.path, "method": lambda: request.method},
    )

    metrics.histogram(
        "api_request_latency_seconds",
        "API request latency",
        labels={"path": lambda: request.path},
    )


def register_routes(app: Flask) -> None:
    """Register main application routes.

    Args:
        app: Flask application instance
    """
    from flask import render_template, send_from_directory

    @app.route("/")
    def index():
        """Render API documentation."""
        return render_template("index.html")

    @app.route("/docs")
    def api_docs():
        """Serve OpenAPI documentation."""
        return render_template("swagger.html")

    @app.route("/openapi.yaml")
    def openapi_spec():
        """Serve OpenAPI specification."""
        return send_from_directory("api", "openapi.yaml")


# Create the application instance
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
