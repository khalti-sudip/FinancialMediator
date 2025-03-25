"""Provider Resource module for managing financial service providers.

This module provides RESTful endpoints for managing financial service providers in the system.
It handles CRUD operations for providers and implements proper validation and error handling.
"""

from typing import Tuple, Dict, Any, Optional, List
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from models import Provider
from api.schemas.provider import ProviderSchema
from api.error_handlers import (
    ResourceNotFoundError,
    ValidationError as APIValidationError,
)
from utils.logging_config import setup_logger

# Set up logger
logger = setup_logger("provider_resource")


class ProviderResource(Resource):
    """Resource for managing individual financial service providers.

    This resource provides endpoints for retrieving, updating, and deleting providers.
    Each provider represents a financial service that can be integrated with the system.

    Endpoints:
        GET /providers/<provider_id>: Retrieve a specific provider
        PUT /providers/<provider_id>: Update a provider's information
        DELETE /providers/<provider_id>: Delete a provider
    """

    @jwt_required()
    def get(self, provider_id: int) -> Tuple[Dict[str, Any], int]:
        """Retrieve a specific provider by ID.

        Args:
            provider_id (int): The unique identifier of the provider

        Returns:
            Tuple[Dict[str, Any], int]: A tuple containing:
                - Dict with provider data including:
                    - id (int): Provider ID
                    - name (str): Provider name
                    - api_key (str): Provider API key
                    - status (str): Provider status
                    - provider_type (str): Type of provider
                    - base_url (str): Provider's base API URL
                - HTTP status code

        Raises:
            ResourceNotFoundError: If the provider is not found
        """
        logger.info(f"Retrieving provider with ID: {provider_id}")

        provider = Provider.query.get(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            raise ResourceNotFoundError(f"Provider with ID {provider_id} not found")

        return ProviderSchema().dump(provider), 200

    @jwt_required()
    def put(self, provider_id: int) -> Tuple[Dict[str, Any], int]:
        """Update a provider's information.

        Args:
            provider_id (int): The unique identifier of the provider

        JSON Payload:
            - name (str, optional): New provider name
            - status (str, optional): New provider status
            - api_key (str, optional): New API key
            - api_secret (str, optional): New API secret
            - base_url (str, optional): New base URL
            - webhook_url (str, optional): New webhook URL

        Returns:
            Tuple[Dict[str, Any], int]: A tuple containing:
                - Dict with updated provider data
                - HTTP status code

        Raises:
            ResourceNotFoundError: If the provider is not found
            ValidationError: If the request data is invalid
        """
        logger.info(f"Updating provider with ID: {provider_id}")

        provider = Provider.query.get(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            raise ResourceNotFoundError(f"Provider with ID {provider_id} not found")

        try:
            schema = ProviderSchema(partial=True)
            data = schema.load(request.get_json())

            for key, value in data.items():
                setattr(provider, key, value)

            db.session.commit()
            logger.info(f"Provider {provider_id} updated successfully")

            return schema.dump(provider), 200

        except ValidationError as e:
            logger.error(
                f"Validation error while updating provider {provider_id}: {e.messages}"
            )
            raise APIValidationError(
                message="Invalid provider data", details=e.messages
            )


class ProviderListResource(Resource):
    """Resource for managing the collection of financial service providers.

    This resource provides endpoints for listing all providers and creating new ones.

    Endpoints:
        GET /providers: List all providers with optional filtering
        POST /providers: Create a new provider
    """

    @jwt_required()
    def get(self) -> Tuple[Dict[str, List[Dict[str, Any]]], int]:
        """List all providers with optional filtering.

        Query Parameters:
            status (str, optional): Filter by provider status
            provider_type (str, optional): Filter by provider type

        Returns:
            Tuple[Dict[str, List[Dict[str, Any]]], int]: A tuple containing:
                - Dict with list of providers
                - HTTP status code
        """
        logger.info("Retrieving list of providers")

        query = Provider.query

        # Apply filters
        status = request.args.get("status")
        if status:
            query = query.filter(Provider.status == status)

        provider_type = request.args.get("provider_type")
        if provider_type:
            query = query.filter(Provider.provider_type == provider_type)

        providers = query.all()
        return {"providers": ProviderSchema(many=True).dump(providers)}, 200

    @jwt_required()
    def post(self) -> Tuple[Dict[str, Any], int]:
        """Create a new provider.

        JSON Payload:
            - name (str): Provider name
            - api_key (str): Provider API key
            - api_secret (str, optional): Provider API secret
            - status (str): Provider status
            - provider_type (str): Type of provider
            - base_url (str): Provider's base API URL
            - webhook_url (str, optional): Provider's webhook URL

        Returns:
            Tuple[Dict[str, Any], int]: A tuple containing:
                - Dict with created provider data
                - HTTP status code

        Raises:
            ValidationError: If the request data is invalid
        """
        logger.info("Creating new provider")

        try:
            schema = ProviderSchema()
            data = schema.load(request.get_json())

            provider = Provider(**data)
            db.session.add(provider)
            db.session.commit()

            logger.info(f"Provider created successfully with ID: {provider.id}")
            return schema.dump(provider), 201

        except ValidationError as e:
            logger.error(f"Validation error while creating provider: {e.messages}")
            raise APIValidationError(
                message="Invalid provider data", details=e.messages
            )


class ProviderDeleteResource(Resource):
    """Resource for deleting financial service providers.

    This resource provides an endpoint for deleting a provider.

    Endpoints:
        DELETE /providers/<provider_id>: Delete a provider
    """

    @jwt_required()
    def delete(self, provider_id: int) -> Tuple[Dict[str, Any], int]:
        """Delete a provider.

        Args:
            provider_id (int): The unique identifier of the provider

        Returns:
            Tuple[Dict[str, Any], int]: A tuple containing the deletion result and HTTP status code

        Raises:
            ResourceNotFoundError: If the provider is not found or has existing transactions
        """
        logger.info(f"Deleting provider with ID: {provider_id}")

        provider = Provider.query.get(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            raise ResourceNotFoundError(f"Provider with ID {provider_id} not found")

        try:
            # Check if there are any active transactions for this provider
            if provider.transactions:
                logger.warning(
                    f"Cannot delete provider {provider_id} with existing transactions"
                )
                raise ResourceNotFoundError(
                    "Cannot delete provider with existing transactions. Set status to inactive instead."
                )

            db.session.delete(provider)
            db.session.commit()
            logger.info(f"Provider {provider_id} deleted successfully")

            return {"message": "Provider deleted successfully"}, 204

        except Exception as e:
            logger.error(f"Unexpected error deleting provider: {str(e)}")
            raise APIValidationError(
                message="An unexpected error occurred", details=str(e)
            )
