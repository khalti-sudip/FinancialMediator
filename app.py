import os
import logging

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_jwt_extended import JWTManager


class Base(DeclarativeBase):
    pass


# Initialize extensions
db = SQLAlchemy(model_class=Base)
jwt = JWTManager()

# Create the Flask application
app = Flask(__name__)
api = Api(app)

# Load configuration
app.config.from_object('config.Config')
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure JWT
app.config['JWT_SECRET_KEY'] = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret")
jwt.init_app(app)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///banking_middleware.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Register API resources
def register_resources():
    from api.resources.transaction import TransactionResource, TransactionListResource
    from api.resources.provider import ProviderResource, ProviderListResource
    from api.resources.status import StatusResource
    from api.resources.auth import AuthResource, TokenRefreshResource
    
    # Transaction endpoints
    api.add_resource(TransactionResource, '/api/v1/transactions/<transaction_id>')
    api.add_resource(TransactionListResource, '/api/v1/transactions')
    
    # Provider endpoints
    api.add_resource(ProviderResource, '/api/v1/providers/<provider_id>')
    api.add_resource(ProviderListResource, '/api/v1/providers')
    
    # Status endpoint
    api.add_resource(StatusResource, '/api/v1/status')
    
    # Auth endpoints
    api.add_resource(AuthResource, '/api/v1/auth')
    api.add_resource(TokenRefreshResource, '/api/v1/auth/refresh')

# Initialize database
with app.app_context():
    # Import models to ensure they're registered with SQLAlchemy
    import models
    
    # Create database tables
    db.create_all()
    
    # Register API resources
    register_resources()
    
    app.logger.info("Banking Middleware API initialized successfully")
