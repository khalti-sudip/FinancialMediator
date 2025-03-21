import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_jwt_extended import JWTManager
from utils.error_handlers import register_error_handlers


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
jwt = JWTManager()

# Set up basic logging before app creation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Set secret key from environment variable
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Configure advanced logging system within the app context
    with app.app_context():
        from utils.logging_config import configure_logging
        configure_logging(app.config.get('LOG_LEVEL', 'INFO'))
    
    # Register blueprints
    from api.middleware import middleware_bp
    from api.auth import auth_bp
    from api.providers import providers_bp
    from api.banking import banking_bp
    
    app.register_blueprint(middleware_bp, url_prefix='/api/v1/middleware')
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(providers_bp, url_prefix='/api/v1/providers')
    app.register_blueprint(banking_bp, url_prefix='/api/v1/banking')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created")
    
    @app.route('/')
    def index():
        """Render the main page"""
        from flask import render_template
        return render_template('index.html')
    
    @app.route('/status')
    def status():
        """Simple status endpoint for monitoring"""
        from flask import render_template
        return render_template('status.html')
    
    logger.info("Application initialized successfully")
    return app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
