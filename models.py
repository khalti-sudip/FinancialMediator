from datetime import datetime
from app import db
from flask_login import UserMixin
from enum import Enum


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(UserMixin, db.Model):
    """User model for API authentication"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(50), default='user')

    def __repr__(self):
        return f'<User {self.username}>'


class Provider(db.Model):
    """Financial service provider model"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    api_key = db.Column(db.String(256))
    api_url = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Boolean, default=True)  # whether the provider is active
    description = db.Column(db.Text)
    config = db.Column(db.JSON)  # store provider-specific configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    transactions = db.relationship('Transaction', backref='provider', lazy=True)

    def __repr__(self):
        return f'<Provider {self.name}>'


class Transaction(db.Model):
    """Transaction model for tracking financial transactions"""
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(128), unique=True)  # ID from external system
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    status = db.Column(db.String(50), default=TransactionStatus.PENDING)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    transaction_type = db.Column(db.String(50), nullable=False)
    request_data = db.Column(db.JSON)  # original request data
    response_data = db.Column(db.JSON)  # response data
    error_message = db.Column(db.Text)
    customer_id = db.Column(db.String(128))  # ID of the customer in the banking system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Transaction {self.id} ({self.status})>'


class ApiLog(db.Model):
    """Log for API requests and responses"""
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(256), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    request_data = db.Column(db.JSON)
    response_data = db.Column(db.JSON)
    status_code = db.Column(db.Integer)
    ip_address = db.Column(db.String(39))  # IPv6 addresses can be up to 39 chars
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    duration_ms = db.Column(db.Float)  # response time in milliseconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    transaction = db.relationship('Transaction', backref='logs')
    user = db.relationship('User', backref='logs')

    def __repr__(self):
        return f'<ApiLog {self.id} {self.endpoint} {self.status_code}>'
