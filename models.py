from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    """User model for authentication"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="user")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def set_password(self, password):
        """Set the password hash"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class ApiKey(db.Model):
    """API key model for tracking external system credentials"""

    __tablename__ = "api_keys"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    key_value = db.Column(db.String(256), nullable=False)
    secret_value = db.Column(db.String(256), nullable=True)
    provider_type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<ApiKey {self.name} - {self.provider_type}>"


class Transaction(db.Model):
    """Transaction model for tracking middleware operations"""

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    source_system = db.Column(db.String(50), nullable=False)
    target_system = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="pending")
    amount = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    user_id = db.Column(db.String(100), nullable=True)
    request_data = db.Column(db.Text, nullable=True)
    response_data = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Transaction {self.transaction_id} - {self.status}>"


class SystemConfig(db.Model):
    """System configuration for providers and integration settings"""

    __tablename__ = "system_config"

    id = db.Column(db.Integer, primary_key=True)
    system_name = db.Column(db.String(100), unique=True, nullable=False)
    system_type = db.Column(db.String(50), nullable=False)
    base_url = db.Column(db.String(256), nullable=False)
    auth_type = db.Column(db.String(50), default="api_key")
    api_key_id = db.Column(db.Integer, db.ForeignKey("api_keys.id"), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    timeout = db.Column(db.Integer, default=30)  # Request timeout in seconds
    retry_count = db.Column(db.Integer, default=3)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationship
    api_key = db.relationship("ApiKey", backref="system_configs")

    def __repr__(self):
        return f"<SystemConfig {self.system_name} - {self.system_type}>"


class AuditLog(db.Model):
    """Audit log for tracking operations and changes"""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    resource_id = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship("User", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} - {self.resource_type} - {self.resource_id}>"
