import logging
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app import db
from models import Transaction
from api.schemas.transaction import TransactionSchema, TransactionRequestSchema
from services.provider_service import process_transaction
from utils.logging_config import setup_logger

# Set up logger
logger = setup_logger('transaction_resource')


class TransactionResource(Resource):
    """Resource for retrieving and managing individual transactions"""
    
    @jwt_required()
    def get(self, transaction_id):
        """Get a specific transaction by ID"""
        logger.info(f"Retrieving transaction with ID: {transaction_id}")
        
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            logger.warning(f"Transaction not found: {transaction_id}")
            return {"error": "Transaction not found"}, 404
            
        return TransactionSchema().dump(transaction), 200
    
    @jwt_required()
    def put(self, transaction_id):
        """Update a transaction status (e.g., retry a failed transaction)"""
        logger.info(f"Updating transaction with ID: {transaction_id}")
        
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            logger.warning(f"Transaction not found: {transaction_id}")
            return {"error": "Transaction not found"}, 404
        
        try:
            # Only allow updating status and error message
            data = request.get_json()
            schema = TransactionSchema(only=["status", "error_message"])
            updates = schema.load(data, partial=True)
            
            for key, value in updates.items():
                setattr(transaction, key, value)
                
            db.session.commit()
            logger.info(f"Transaction {transaction_id} updated successfully")
            
            return TransactionSchema().dump(transaction), 200
            
        except ValidationError as err:
            logger.error(f"Validation error: {err.messages}")
            return {"error": err.messages}, 400
        except Exception as e:
            logger.exception(f"Error updating transaction: {str(e)}")
            db.session.rollback()
            return {"error": "Failed to update transaction"}, 500


class TransactionListResource(Resource):
    """Resource for listing and creating transactions"""
    
    @jwt_required()
    def get(self):
        """List all transactions with optional filtering"""
        logger.info("Retrieving transaction list")
        
        # Parse query parameters for filtering
        status = request.args.get('status')
        provider_id = request.args.get('provider_id')
        customer_id = request.args.get('customer_id')
        
        # Build the query with filters
        query = Transaction.query
        
        if status:
            query = query.filter(Transaction.status == status)
        if provider_id:
            query = query.filter(Transaction.provider_id == provider_id)
        if customer_id:
            query = query.filter(Transaction.customer_id == customer_id)
            
        # Get paginated results
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Limit max per_page to 100 to prevent overloading
        per_page = min(per_page, 100)
        
        paginated_transactions = query.order_by(Transaction.created_at.desc()).paginate(
            page=page, per_page=per_page
        )
        
        # Prepare the response
        result = {
            "items": TransactionSchema(many=True).dump(paginated_transactions.items),
            "total": paginated_transactions.total,
            "page": page,
            "per_page": per_page,
            "pages": paginated_transactions.pages
        }
        
        return result, 200
    
    @jwt_required()
    def post(self):
        """Create a new transaction"""
        logger.info("Creating new transaction")
        
        try:
            # Validate and parse the incoming request
            data = request.get_json()
            transaction_request = TransactionRequestSchema().load(data)
            
            # Process the transaction through the appropriate provider
            result = process_transaction(transaction_request)
            
            return TransactionSchema().dump(result), 201
            
        except ValidationError as err:
            logger.error(f"Validation error: {err.messages}")
            return {"error": err.messages}, 400
        except Exception as e:
            logger.exception(f"Error processing transaction: {str(e)}")
            return {"error": str(e)}, 500
