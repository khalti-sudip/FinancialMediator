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
providers_bp = Blueprint("providers", __name__)


class ProviderConfigSchema(Schema):
    """Schema for validating provider configuration"""

    system_name = fields.String(required=True)
    base_url = fields.Url(required=True)
    auth_type = fields.String(default="api_key")
    api_key = fields.String(required=False)
    api_secret = fields.String(required=False)
    timeout = fields.Integer(default=30)
    retry_count = fields.Integer(default=3)


def execute_provider_request(request_data, provider_config):
    """
    Execute a request to a financial service provider

    Args:
        request_data (dict): The transformed request data to send
        provider_config (SystemConfig): The provider configuration object

    Returns:
        tuple: (response_data, status_code)
    """
    logger.debug(f"Executing request to provider: {provider_config.system_name}")

    # Get API key for this provider
    api_key = None
    if provider_config.api_key_id:
        api_key = ApiKey.query.get(provider_config.api_key_id)

    if not api_key and provider_config.auth_type != "none":
        logger.error(f"API key not found for provider {provider_config.system_name}")
        return {"error": "API key configuration missing"}, 500

    # Prepare headers
    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    # Add authentication based on auth_type
    if provider_config.auth_type == "api_key":
        headers["X-API-Key"] = api_key.key_value
    elif provider_config.auth_type == "bearer":
        headers["Authorization"] = f"Bearer {api_key.key_value}"
    elif provider_config.auth_type == "basic":
        # Basic auth would be handled through requests auth parameter
        pass
    elif provider_config.auth_type == "hmac":
        # Sign the request using HMAC
        signature = sign_request(json.dumps(request_data), api_key.secret_value)
        headers["X-Signature"] = signature

    # Determine endpoint based on transaction type
    transaction_type = request_data.get("transaction_type", "")
    endpoint = f"{provider_config.base_url}/api/{transaction_type.lower()}"

    # Add request parameters
    params = request_data.get("params", {})

    # Set timeout and retry configuration
    timeout = provider_config.timeout
    max_retries = provider_config.retry_count

    # Execute the request with retry logic
    retry_count = 0
    while retry_count <= max_retries:
        try:
            if request_data.get("method", "POST").upper() == "GET":
                response = requests.get(
                    endpoint, params=params, headers=headers, timeout=timeout
                )
            else:
                response = requests.post(
                    endpoint,
                    json=request_data.get("payload", {}),
                    params=params,
                    headers=headers,
                    timeout=timeout,
                )

            # Log the response status
            logger.debug(f"Provider response status: {response.status_code}")

            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                logger.warning(f"Provider response is not JSON: {response.text[:100]}")
                response_data = {"raw_response": response.text}

            return response_data, response.status_code

        except requests.exceptions.Timeout:
            logger.warning(
                f"Request timeout to provider {provider_config.system_name}, attempt {retry_count + 1}/{max_retries + 1}"
            )
            retry_count += 1
            if retry_count <= max_retries:
                # Exponential backoff
                time.sleep(2**retry_count)
            else:
                logger.error(
                    f"Max retries reached for provider {provider_config.system_name}"
                )
                return {"error": "Request timeout after retries"}, 504

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Request error to provider {provider_config.system_name}: {str(e)}"
            )
            return {"error": f"Request failed: {str(e)}"}, 500


@providers_bp.route("/config", methods=["POST"])
@jwt_required()
def create_provider_config():
    """Create a new financial service provider configuration"""
    current_user = get_jwt_identity()
    logger.info(f"Creating provider configuration by user {current_user}")

    try:
        # Validate request data
        schema = ProviderConfigSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            logger.warning(f"Provider config validation error: {err.messages}")
            return (
                jsonify(
                    {"error": "Invalid provider configuration", "details": err.messages}
                ),
                400,
            )

        system_name = data["system_name"]

        # Check if provider already exists
        existing_provider = SystemConfig.query.filter_by(
            system_name=system_name
        ).first()
        if existing_provider:
            logger.warning(f"Provider {system_name} already exists")
            return jsonify({"error": f"Provider {system_name} already exists"}), 409

        # Create API key if provided
        api_key_id = None
        if "api_key" in data:
            api_key = ApiKey(
                name=f"{system_name}_key",
                key_value=data["api_key"],
                secret_value=data.get("api_secret"),
                provider_type="financial_provider",
                is_active=True,
            )
            db.session.add(api_key)
            db.session.flush()  # Get the ID without committing
            api_key_id = api_key.id

        # Create provider config
        provider_config = SystemConfig(
            system_name=system_name,
            system_type="financial_provider",
            base_url=data["base_url"],
            auth_type=data["auth_type"],
            api_key_id=api_key_id,
            timeout=data.get("timeout", 30),
            retry_count=data.get("retry_count", 3),
            is_active=True,
        )

        db.session.add(provider_config)
        db.session.commit()

        logger.info(f"Provider configuration created: {system_name}")
        return (
            jsonify(
                {
                    "message": "Provider configuration created successfully",
                    "provider": {
                        "id": provider_config.id,
                        "system_name": provider_config.system_name,
                        "system_type": provider_config.system_type,
                        "base_url": provider_config.base_url,
                        "auth_type": provider_config.auth_type,
                        "timeout": provider_config.timeout,
                        "retry_count": provider_config.retry_count,
                        "is_active": provider_config.is_active,
                    },
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error creating provider configuration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@providers_bp.route("/config/<provider_name>", methods=["GET"])
@jwt_required()
def get_provider_config(provider_name):
    """Get configuration for a specific provider"""
    current_user = get_jwt_identity()
    logger.info(
        f"Retrieving provider {provider_name} configuration by user {current_user}"
    )

    try:
        provider_config = SystemConfig.query.filter_by(
            system_name=provider_name, system_type="financial_provider"
        ).first()

        if not provider_config:
            logger.warning(f"Provider {provider_name} not found")
            return jsonify({"error": f"Provider {provider_name} not found"}), 404

        result = {
            "id": provider_config.id,
            "system_name": provider_config.system_name,
            "system_type": provider_config.system_type,
            "base_url": provider_config.base_url,
            "auth_type": provider_config.auth_type,
            "timeout": provider_config.timeout,
            "retry_count": provider_config.retry_count,
            "is_active": provider_config.is_active,
        }

        logger.info(f"Retrieved provider configuration: {provider_name}")
        return jsonify({"provider": result}), 200

    except Exception as e:
        logger.exception(f"Error retrieving provider configuration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@providers_bp.route("/config", methods=["GET"])
@jwt_required()
def get_all_providers():
    """Get all financial service provider configurations"""
    current_user = get_jwt_identity()
    logger.info(f"Retrieving all provider configurations by user {current_user}")

    try:
        providers = SystemConfig.query.filter_by(system_type="financial_provider").all()

        results = [
            {
                "id": provider.id,
                "system_name": provider.system_name,
                "base_url": provider.base_url,
                "auth_type": provider.auth_type,
                "timeout": provider.timeout,
                "retry_count": provider.retry_count,
                "is_active": provider.is_active,
            }
            for provider in providers
        ]

        logger.info(f"Retrieved {len(results)} provider configurations")
        return jsonify({"providers": results}), 200

    except Exception as e:
        logger.exception(f"Error retrieving provider configurations: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@providers_bp.route("/config/<provider_name>", methods=["PUT"])
@jwt_required()
def update_provider_config(provider_name):
    """Update an existing provider configuration"""
    current_user = get_jwt_identity()
    logger.info(
        f"Updating provider {provider_name} configuration by user {current_user}"
    )

    try:
        provider_config = SystemConfig.query.filter_by(
            system_name=provider_name, system_type="financial_provider"
        ).first()

        if not provider_config:
            logger.warning(f"Provider {provider_name} not found")
            return jsonify({"error": f"Provider {provider_name} not found"}), 404

        # Validate request data
        schema = ProviderConfigSchema()
        try:
            data = schema.load(request.json)
        except ValidationError as err:
            logger.warning(f"Provider config validation error: {err.messages}")
            return (
                jsonify(
                    {"error": "Invalid provider configuration", "details": err.messages}
                ),
                400,
            )

        # Update API key if provided
        if "api_key" in data:
            if provider_config.api_key_id:
                # Update existing API key
                api_key = ApiKey.query.get(provider_config.api_key_id)
                if api_key:
                    api_key.key_value = data["api_key"]
                    api_key.secret_value = data.get("api_secret")
            else:
                # Create new API key
                api_key = ApiKey(
                    name=f"{provider_name}_key",
                    key_value=data["api_key"],
                    secret_value=data.get("api_secret"),
                    provider_type="financial_provider",
                    is_active=True,
                )
                db.session.add(api_key)
                db.session.flush()
                provider_config.api_key_id = api_key.id

        # Update provider config
        provider_config.base_url = data["base_url"]
        provider_config.auth_type = data["auth_type"]
        provider_config.timeout = data.get("timeout", 30)
        provider_config.retry_count = data.get("retry_count", 3)

        db.session.commit()

        logger.info(f"Provider configuration updated: {provider_name}")
        return (
            jsonify(
                {
                    "message": "Provider configuration updated successfully",
                    "provider": {
                        "id": provider_config.id,
                        "system_name": provider_config.system_name,
                        "system_type": provider_config.system_type,
                        "base_url": provider_config.base_url,
                        "auth_type": provider_config.auth_type,
                        "timeout": provider_config.timeout,
                        "retry_count": provider_config.retry_count,
                        "is_active": provider_config.is_active,
                    },
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        logger.exception(f"Error updating provider configuration: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@providers_bp.route("/test-connection/<provider_name>", methods=["POST"])
@jwt_required()
def test_provider_connection(provider_name):
    """Test connection to a financial service provider"""
    current_user = get_jwt_identity()
    logger.info(
        f"Testing connection to provider {provider_name} by user {current_user}"
    )

    try:
        provider_config = SystemConfig.query.filter_by(
            system_name=provider_name, system_type="financial_provider"
        ).first()

        if not provider_config:
            logger.warning(f"Provider {provider_name} not found")
            return jsonify({"error": f"Provider {provider_name} not found"}), 404

        # Prepare test request data
        test_data = {
            "transaction_type": "test",
            "method": "GET",
            "payload": {},
            "params": {"test": "true"},
        }

        # Execute test request
        response, status_code = execute_provider_request(test_data, provider_config)

        if status_code >= 200 and status_code < 300:
            logger.info(f"Test connection to provider {provider_name} successful")
            return (
                jsonify(
                    {
                        "message": "Connection successful",
                        "status_code": status_code,
                        "response": response,
                    }
                ),
                200,
            )
        else:
            logger.warning(
                f"Test connection to provider {provider_name} failed with status {status_code}"
            )
            return (
                jsonify(
                    {
                        "error": "Connection failed",
                        "status_code": status_code,
                        "response": response,
                    }
                ),
                400,
            )

    except Exception as e:
        logger.exception(f"Error testing provider connection: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
