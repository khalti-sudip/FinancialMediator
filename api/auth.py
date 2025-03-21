import logging
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity
)
from marshmallow import Schema, fields, validate, ValidationError

from app import db
from models import User
from utils.security import verify_request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)


# Define schemas for request validation
class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class RegisterSchema(Schema):
    username = fields.String(
        required=True, 
        validate=validate.Length(min=3, max=64)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True, 
        validate=validate.Length(min=8, max=128)
    )
    role = fields.String(
        validate=validate.OneOf(['user', 'admin']), 
        default='user'
    )


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and issue JWT tokens"""
    try:
        # Validate request data
        schema = LoginSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            logger.warning(f"Login validation error: {err.messages}")
            return jsonify({"error": "Invalid login data", "details": err.messages}), 400
        
        username = data['username']
        password = data['password']
        
        # Find the user
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            logger.warning(f"Failed login attempt for username: {username}")
            return jsonify({"error": "Invalid username or password"}), 401
        
        if not user.is_active:
            logger.warning(f"Login attempt for inactive user: {username}")
            return jsonify({"error": "Account is inactive"}), 403
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        logger.info(f"User {username} logged in successfully")
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200
    
    except Exception as e:
        logger.exception(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        # Validate request data
        schema = RegisterSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            logger.warning(f"Registration validation error: {err.messages}")
            return jsonify({"error": "Invalid registration data", "details": err.messages}), 400
        
        username = data['username']
        email = data['email']
        
        # Check if user or email already exists
        if User.query.filter_by(username=username).first():
            logger.warning(f"Registration attempt with existing username: {username}")
            return jsonify({"error": "Username already exists"}), 409
        
        if User.query.filter_by(email=email).first():
            logger.warning(f"Registration attempt with existing email: {email}")
            return jsonify({"error": "Email already exists"}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=data.get('role', 'user')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"New user registered: {username}")
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 201
    
    except Exception as e:
        logger.exception(f"Registration error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            logger.warning(f"Token refresh attempt for inactive or non-existent user ID: {current_user_id}")
            return jsonify({"error": "User not found or inactive"}), 401
        
        # Create new access token
        access_token = create_access_token(identity=current_user_id)
        
        logger.info(f"Access token refreshed for user ID: {current_user_id}")
        return jsonify({"access_token": access_token}), 200
    
    except Exception as e:
        logger.exception(f"Token refresh error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_token():
    """Verify that the current token is valid"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            logger.warning(f"Token verification failed for user ID: {current_user_id}")
            return jsonify({"error": "User not found or inactive"}), 401
        
        logger.info(f"Token verified for user ID: {current_user_id}")
        return jsonify({
            "valid": True,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }), 200
    
    except Exception as e:
        logger.exception(f"Token verification error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/api-key', methods=['POST'])
@jwt_required()
def generate_api_key():
    """Generate an API key for external system integrations"""
    try:
        # This endpoint would typically generate API keys for external systems 
        # For now, it's a placeholder that could be implemented based on requirements
        return jsonify({"message": "API key generation not implemented yet"}), 501
    
    except Exception as e:
        logger.exception(f"API key generation error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
