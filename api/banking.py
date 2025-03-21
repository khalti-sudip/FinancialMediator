import logging
import json
import time
import requests
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError

from app import db
from models import SystemConfig, ApiKey, Transaction
from utils.security import sign_request

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
banking_bp = Blueprint('banking', __name__)


class BankingConfigSchema(Schema):
    """Schema for validating banking system configuration"""
    system_name = fields.String(required=True)
    base_url = fields.Url(required=True)
    auth_type = fields.String(default='api_key')
    api_key = fields.String(required=False)
    api_secret = fields.String(required=False)
    timeout = fields.Integer(default=30)
    retry_count = fields.Integer(default=3)


def execute_banking_request(request_data, banking_config):
    """
    Execute a request to a banking system
    
    Args:
        request_data (dict): The transformed request data to send
        banking_config (SystemConfig): The banking system configuration object
    
    Returns:
        tuple: (response_data, status_code)
    """
    logger.debug(f"Executing request to banking system: {banking_config.system_name}")
    
    # Get API key for this banking system
    api_key = None
    if banking_config.api_key_id:
        api_key = ApiKey.query.get(banking_config.api_key_id)
    
    if not api_key and banking_config.auth_type != 'none':
        logger.error(f"API key not found for banking system {banking_config.system_name}")
        return {"error": "API key configuration missing"}, 500
    
    # Prepare headers
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # Add authentication based on auth_type
    if banking_config.auth_type == 'api_key':
        headers['X-API-Key'] = api_key.key_value
    elif banking_config.auth_type == 'bearer':
        headers['Authorization'] = f"Bearer {api_key.key_value}"
    elif banking_config.auth_type == 'basic':
        # Basic auth would be handled through requests auth parameter
        pass
    elif banking_config.auth_type == 'hmac':
        # Sign the request using HMAC
        signature = sign_request(json.dumps(request_data), api_key.secret_value)
        headers['X-Signature'] = signature
    
    # Determine endpoint based on transaction type
    transaction_type = request_data.get('transaction_type', '')
    endpoint = f"{banking_config.base_url}/api/{transaction_type.lower()}"
    
    # Add request parameters
    params = request_data.get('params', {})
    
    # Set timeout and retry configuration
    timeout = banking_config.timeout
    max_retries = banking_config.retry_count
    
    # Execute the request with retry logic
    retry_count = 0
    while retry_count <= max_retries:
        try:
            if request_data.get('method', 'POST').upper() == 'GET':
                response = requests.get(
                    endpoint,
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            else:
                response = requests.post(
                    endpoint,
                    json=request_data.get('payload', {}),
                    params=params,
                    headers=headers,
                    timeout=timeout
                )
            
            # Log the response status
            logger.debug(f"Banking system response status: {response.status_code}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                logger.warning(f"Banking system response is not JSON: {response.text[:100]}")
                response_data = {"raw_response": response.text}
            
            return response_data, response.status_code
            
        except requests.exceptions.Timeout:
            logger.warning(f"Request timeout to banking system {banking_config.system_name}, attempt {retry_count + 1}/{max_retries + 1}")
            retry_count += 1
            if retry_count <= max_retries:
                # Exponential backoff
                time.sleep(2 ** retry_count)
            else:
                logger.error(f"Max retries reached for banking system {banking_config.system_name}")
                return {"error": "Request timeout after retries"}, 504
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error to banking system {banking_config.system_name}: {str(e)}")
            return {"error": f"Request failed: {str(e)}"}, 500


@banking_bp.route('/config', methods=['POST'])
@jwt_required()
def create_banking_config():
    """Create a new banking system configuration"""
    current_user = get_jwt_identity()
    logger.info(f"Creating banking system configuration by user {current_user}")
    
    try:
        # Validate request data
        schema = BankingConfigSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            logger.warning(f"Banking config validation error: {err.messages}")
            return jsonify({"error": "Invalid banking system configuration", "details": err.messages}), 400
        
        system_name = data['system_name']
        
        # Check if banking system already exists
        existing_system = SystemConfig.query.filter_by(system_name=system_name).first()
        if existing_system:
            logger.warning(f"Banking system {system_name} already exists")
            return jsonify({"error": f"Banking system {system_name} already exists"}), 409
        
        # Create API key if provided
        api_key_id = None
        if 'api_key' in data:
            api_key = ApiKey(
                name=f"{system_name}_key",
                key_value=data['api_key'],
                secret_value=data.get('api_secret'),
                provider_type='banking_system',
                is_active=True
            )
            db.session.add(api_key)
            db.session.flush()  # Get the ID without committing
            api_key_id = api_key.id
        
        # Create banking system config
        banking_config = SystemConfig(
            system_name=system_name,
            system_type='banking_system',
            base_url=data['base_url'],
            auth_type=data['auth_type'],
            api_key_id=api_key_id,
            timeout=data.get('timeout', 30),
            retry_count=data.get('retry_count', 3),
            is_active=True
        )
        
        db.session.add(banking_config)
        db.session.commit()
        
        logger.info(f"Banking system configuration created: {system_name}")
        return jsonify({
            "message": "Banking system configuration created successfully",
            "banking_system": {
                "id": banking_config.id,
                "system_name": banking_config.system_name,
                "system_type": banking_config.system_type,
                "base_url": banking_config.base_url,
                "auth_type": banking_config.auth_type,
                "timeout": banking_config.timeout,
                "retry_count": banking_config.retry_count,
                "is_active": banking_config.is_active
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error creating banking system configuration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@banking_bp.route('/config/<system_name>', methods=['GET'])
@jwt_required()
def get_banking_config(system_name):
    """Get configuration for a specific banking system"""
    current_user = get_jwt_identity()
    logger.info(f"Retrieving banking system {system_name} configuration by user {current_user}")
    
    try:
        banking_config = SystemConfig.query.filter_by(
            system_name=system_name, 
            system_type='banking_system'
        ).first()
        
        if not banking_config:
            logger.warning(f"Banking system {system_name} not found")
            return jsonify({"error": f"Banking system {system_name} not found"}), 404
        
        result = {
            "id": banking_config.id,
            "system_name": banking_config.system_name,
            "system_type": banking_config.system_type,
            "base_url": banking_config.base_url,
            "auth_type": banking_config.auth_type,
            "timeout": banking_config.timeout,
            "retry_count": banking_config.retry_count,
            "is_active": banking_config.is_active
        }
        
        logger.info(f"Retrieved banking system configuration: {system_name}")
        return jsonify({"banking_system": result}), 200
    
    except Exception as e:
        logger.exception(f"Error retrieving banking system configuration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@banking_bp.route('/config', methods=['GET'])
@jwt_required()
def get_all_banking_systems():
    """Get all banking system configurations"""
    current_user = get_jwt_identity()
    logger.info(f"Retrieving all banking system configurations by user {current_user}")
    
    try:
        banking_systems = SystemConfig.query.filter_by(system_type='banking_system').all()
        
        results = [{
            "id": system.id,
            "system_name": system.system_name,
            "base_url": system.base_url,
            "auth_type": system.auth_type,
            "timeout": system.timeout,
            "retry_count": system.retry_count,
            "is_active": system.is_active
        } for system in banking_systems]
        
        logger.info(f"Retrieved {len(results)} banking system configurations")
        return jsonify({"banking_systems": results}), 200
    
    except Exception as e:
        logger.exception(f"Error retrieving banking system configurations: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@banking_bp.route('/config/<system_name>', methods=['PUT'])
@jwt_required()
def update_banking_config(system_name):
    """Update an existing banking system configuration"""
    current_user = get_jwt_identity()
    logger.info(f"Updating banking system {system_name} configuration by user {current_user}")
    
    try:
        banking_config = SystemConfig.query.filter_by(
            system_name=system_name, 
            system_type='banking_system'
        ).first()
        
        if not banking_config:
            logger.warning(f"Banking system {system_name} not found")
            return jsonify({"error": f"Banking system {system_name} not found"}), 404
        
        # Validate request data
        schema = BankingConfigSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            logger.warning(f"Banking system config validation error: {err.messages}")
            return jsonify({"error": "Invalid banking system configuration", "details": err.messages}), 400
        
        # Update API key if provided
        if 'api_key' in data:
            if banking_config.api_key_id:
                # Update existing API key
                api_key = ApiKey.query.get(banking_config.api_key_id)
                if api_key:
                    api_key.key_value = data['api_key']
                    api_key.secret_value = data.get('api_secret')
            else:
                # Create new API key
                api_key = ApiKey(
                    name=f"{system_name}_key",
                    key_value=data['api_key'],
                    secret_value=data.get('api_secret'),
                    provider_type='banking_system',
                    is_active=True
                )
                db.session.add(api_key)
                db.session.flush()
                banking_config.api_key_id = api_key.id
        
        # Update banking config
        banking_config.base_url = data['base_url']
        banking_config.auth_type = data['auth_type']
        banking_config.timeout = data.get('timeout', 30)
        banking_config.retry_count = data.get('retry_count', 3)
        
        db.session.commit()
        
        logger.info(f"Banking system configuration updated: {system_name}")
        return jsonify({
            "message": "Banking system configuration updated successfully",
            "banking_system": {
                "id": banking_config.id,
                "system_name": banking_config.system_name,
                "system_type": banking_config.system_type,
                "base_url": banking_config.base_url,
                "auth_type": banking_config.auth_type,
                "timeout": banking_config.timeout,
                "retry_count": banking_config.retry_count,
                "is_active": banking_config.is_active
            }
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating banking system configuration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@banking_bp.route('/test-connection/<system_name>', methods=['POST'])
@jwt_required()
def test_banking_connection(system_name):
    """Test connection to a banking system"""
    current_user = get_jwt_identity()
    logger.info(f"Testing connection to banking system {system_name} by user {current_user}")
    
    try:
        banking_config = SystemConfig.query.filter_by(
            system_name=system_name, 
            system_type='banking_system'
        ).first()
        
        if not banking_config:
            logger.warning(f"Banking system {system_name} not found")
            return jsonify({"error": f"Banking system {system_name} not found"}), 404
        
        # Prepare test request data
        test_data = {
            'transaction_type': 'test',
            'method': 'GET',
            'payload': {},
            'params': {
                'test': 'true'
            }
        }
        
        # Execute test request
        response, status_code = execute_banking_request(test_data, banking_config)
        
        if status_code >= 200 and status_code < 300:
            logger.info(f"Test connection to banking system {system_name} successful")
            return jsonify({
                "message": "Connection successful",
                "status_code": status_code,
                "response": response
            }), 200
        else:
            logger.warning(f"Test connection to banking system {system_name} failed with status {status_code}")
            return jsonify({
                "error": "Connection failed",
                "status_code": status_code,
                "response": response
            }), 400
    
    except Exception as e:
        logger.exception(f"Error testing banking system connection: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
