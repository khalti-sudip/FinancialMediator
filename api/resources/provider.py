import logging
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from models import Provider
from api.schemas.provider import ProviderSchema
from utils.logging_config import setup_logger

# Set up logger
logger = setup_logger('provider_resource')


class ProviderResource(Resource):
    """Resource for managing individual financial service providers"""
    
    @jwt_required()
    def get(self, provider_id):
        """Get a specific provider by ID"""
        logger.info(f"Retrieving provider with ID: {provider_id}")
        
        provider = Provider.query.get(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            return {"error": "Provider not found"}, 404
            
        return ProviderSchema().dump(provider), 200
    
    @jwt_required()
    def put(self, provider_id):
        """Update a provider"""
        logger.info(f"Updating provider with ID: {provider_id}")
        
        provider = Provider.query.get(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            return {"error": "Provider not found"}, 404
        
        try:
            data = request.get_json()
            updates = ProviderSchema().load(data, partial=True)
            
            for key, value in updates.items():
                setattr(provider, key, value)
                
            db.session.commit()
            logger.info(f"Provider {provider_id} updated successfully")
            
            return ProviderSchema().dump(provider), 200
            
        except ValidationError as err:
            logger.error(f"Validation error: {err.messages}")
            return {"error": err.messages}, 400
        except Exception as e:
            logger.exception(f"Error updating provider: {str(e)}")
            db.session.rollback()
            return {"error": "Failed to update provider"}, 500
    
    @jwt_required()
    def delete(self, provider_id):
        """Delete a provider"""
        logger.info(f"Deleting provider with ID: {provider_id}")
        
        provider = Provider.query.get(provider_id)
        if not provider:
            logger.warning(f"Provider not found: {provider_id}")
            return {"error": "Provider not found"}, 404
        
        try:
            # Check if there are any active transactions for this provider
            if provider.transactions:
                logger.warning(f"Cannot delete provider {provider_id} with existing transactions")
                return {
                    "error": "Cannot delete provider with existing transactions. Set status to inactive instead."
                }, 400
            
            db.session.delete(provider)
            db.session.commit()
            logger.info(f"Provider {provider_id} deleted successfully")
            
            return {"message": "Provider deleted successfully"}, 204
            
        except Exception as e:
            logger.exception(f"Error deleting provider: {str(e)}")
            db.session.rollback()
            return {"error": "Failed to delete provider"}, 500


class ProviderListResource(Resource):
    """Resource for listing and creating financial service providers"""
    
    @jwt_required()
    def get(self):
        """List all providers with optional filtering"""
        logger.info("Retrieving provider list")
        
        # Parse query parameters for filtering
        status = request.args.get('status')
        name = request.args.get('name')
        
        # Build the query with filters
        query = Provider.query
        
        if status is not None:
            status_bool = status.lower() == 'true'
            query = query.filter(Provider.status == status_bool)
        if name:
            query = query.filter(Provider.name.ilike(f'%{name}%'))
            
        # Get paginated results
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limit max per_page to 100 to prevent overloading
        per_page = min(per_page, 100)
        
        paginated_providers = query.order_by(Provider.name).paginate(
            page=page, per_page=per_page
        )
        
        # Prepare the response
        result = {
            "items": ProviderSchema(many=True).dump(paginated_providers.items),
            "total": paginated_providers.total,
            "page": page,
            "per_page": per_page,
            "pages": paginated_providers.pages
        }
        
        return result, 200
    
    @jwt_required()
    def post(self):
        """Create a new provider"""
        logger.info("Creating new provider")
        
        try:
            data = request.get_json()
            provider_data = ProviderSchema().load(data)
            
            # Create new provider
            provider = Provider(**provider_data)
            db.session.add(provider)
            db.session.commit()
            
            logger.info(f"Provider created with ID: {provider.id}")
            return ProviderSchema().dump(provider), 201
            
        except ValidationError as err:
            logger.error(f"Validation error: {err.messages}")
            return {"error": err.messages}, 400
        except Exception as e:
            logger.exception(f"Error creating provider: {str(e)}")
            db.session.rollback()
            return {"error": "Failed to create provider"}, 500
