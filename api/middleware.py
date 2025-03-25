import logging
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app import db
from models import Transaction, SystemConfig
from api.validation import TransactionSchema, validate_transaction_request
from api.transformers import transform_request, transform_response
from api.providers import execute_provider_request
from api.banking import execute_banking_request
from api.cache import cache_response, get_cached_response
from utils.security import verify_request_signature

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
middleware_bp = Blueprint("middleware", __name__)


@middleware_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for the middleware service."""
    return jsonify({"status": "healthy", "service": "banking_middleware"}), 200


@middleware_bp.route("/transaction", methods=["POST"])
@jwt_required()
def process_transaction():
    """
    Process a transaction between a financial service provider and banking system.
    This endpoint receives transaction data, validates it, transforms it for the
    target system, executes the transaction, and returns the response.
    """
    current_user = get_jwt_identity()
    logger.info(f"Processing transaction request from user {current_user}")

    try:
        # Validate the request structure
        schema = TransactionSchema()
        try:
            transaction_data = schema.load(request.json)
        except ValidationError as err:
            logger.error(f"Validation error: {err.messages}")
            return (
                jsonify({"error": "Invalid request data", "details": err.messages}),
                400,
            )

        # Generate a unique transaction ID
        transaction_id = str(uuid.uuid4())
        transaction_data["transaction_id"] = transaction_id

        # Business validation
        validation_errors = validate_transaction_request(transaction_data)
        if validation_errors:
            logger.error(f"Business validation error: {validation_errors}")
            return (
                jsonify(
                    {
                        "error": "Transaction validation failed",
                        "details": validation_errors,
                    }
                ),
                400,
            )

        # Check if we have the necessary system configurations
        source_system = SystemConfig.query.filter_by(
            system_name=transaction_data["source_system"], is_active=True
        ).first()

        target_system = SystemConfig.query.filter_by(
            system_name=transaction_data["target_system"], is_active=True
        ).first()

        if not source_system or not target_system:
            logger.error(
                f"System configuration not found or inactive for source: {transaction_data['source_system']} or target: {transaction_data['target_system']}"
            )
            return jsonify({"error": "System configuration not found or inactive"}), 400

        # Create a transaction record
        transaction = Transaction(
            transaction_id=transaction_id,
            source_system=transaction_data["source_system"],
            target_system=transaction_data["target_system"],
            transaction_type=transaction_data["transaction_type"],
            status="pending",
            amount=transaction_data.get("amount"),
            currency=transaction_data.get("currency"),
            user_id=current_user,
            request_data=str(transaction_data),
        )
        db.session.add(transaction)
        db.session.commit()

        # Check cache for identical recent transactions if appropriate
        if transaction_data.get("cacheable", False):
            cached_response = get_cached_response(transaction_data)
            if cached_response:
                logger.info(
                    f"Returning cached response for transaction: {transaction_id}"
                )
                # Update transaction status to completed
                transaction.status = "completed"
                transaction.response_data = str(cached_response)
                db.session.commit()
                return jsonify(cached_response), 200

        # Transform the request for the target system
        transformed_request = transform_request(
            transaction_data, source_system, target_system
        )

        # Process based on target system type
        if target_system.system_type == "financial_provider":
            result, status_code = execute_provider_request(
                transformed_request, target_system
            )
        elif target_system.system_type == "banking_system":
            result, status_code = execute_banking_request(
                transformed_request, target_system
            )
        else:
            logger.error(f"Unsupported target system type: {target_system.system_type}")
            transaction.status = "failed"
            transaction.error_message = (
                f"Unsupported target system type: {target_system.system_type}"
            )
            db.session.commit()
            return jsonify({"error": "Unsupported target system type"}), 400

        # Check if the request was successful
        if status_code >= 200 and status_code < 300:
            # Transform the response for the source system
            transformed_response = transform_response(
                result, target_system, source_system
            )

            # Update transaction status
            transaction.status = "completed"
            transaction.response_data = str(transformed_response)
            db.session.commit()

            # Cache successful responses if appropriate
            if transaction_data.get("cacheable", False):
                cache_response(transaction_data, transformed_response)

            logger.info(f"Transaction processed successfully: {transaction_id}")
            return jsonify(transformed_response), 200
        else:
            # Handle error response
            transaction.status = "failed"
            transaction.error_message = str(result.get("error", "Unknown error"))
            db.session.commit()

            logger.error(
                f"Transaction failed: {transaction_id}, Error: {result.get('error', 'Unknown error')}"
            )
            return (
                jsonify({"error": "Transaction processing failed", "details": result}),
                status_code,
            )

    except Exception as e:
        logger.exception(f"Unexpected error processing transaction: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@middleware_bp.route("/status/<transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction_status(transaction_id):
    """Get the status of a specific transaction"""
    current_user = get_jwt_identity()
    logger.info(
        f"Retrieving transaction status for {transaction_id} by user {current_user}"
    )

    try:
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()

        if not transaction:
            logger.warning(f"Transaction not found: {transaction_id}")
            return jsonify({"error": "Transaction not found"}), 404

        result = {
            "transaction_id": transaction.transaction_id,
            "status": transaction.status,
            "transaction_type": transaction.transaction_type,
            "source_system": transaction.source_system,
            "target_system": transaction.target_system,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat(),
        }

        # Include error message if available
        if transaction.error_message:
            result["error_message"] = transaction.error_message

        logger.info(f"Transaction status retrieved: {transaction_id}")
        return jsonify(result), 200

    except Exception as e:
        logger.exception(f"Error retrieving transaction status: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@middleware_bp.route("/transactions", methods=["GET"])
@jwt_required()
def get_transactions():
    """Get a list of transactions with optional filtering"""
    current_user = get_jwt_identity()
    logger.info(f"Retrieving transactions list for user {current_user}")

    try:
        # Get filter parameters
        status = request.args.get("status")
        source_system = request.args.get("source_system")
        target_system = request.args.get("target_system")
        transaction_type = request.args.get("transaction_type")

        # Basic pagination
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 20))

        # Build the query
        query = Transaction.query

        if status:
            query = query.filter_by(status=status)
        if source_system:
            query = query.filter_by(source_system=source_system)
        if target_system:
            query = query.filter_by(target_system=target_system)
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)

        # Apply pagination and get results
        pagination = query.order_by(Transaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        transactions = pagination.items

        results = [
            {
                "transaction_id": tx.transaction_id,
                "status": tx.status,
                "transaction_type": tx.transaction_type,
                "source_system": tx.source_system,
                "target_system": tx.target_system,
                "amount": tx.amount,
                "currency": tx.currency,
                "created_at": tx.created_at.isoformat(),
                "updated_at": tx.updated_at.isoformat(),
            }
            for tx in transactions
        ]

        meta = {
            "page": page,
            "per_page": per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }

        logger.info(f"Retrieved {len(results)} transactions")
        return jsonify({"transactions": results, "meta": meta}), 200

    except Exception as e:
        logger.exception(f"Error retrieving transactions: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@middleware_bp.route("/webhook", methods=["POST"])
def process_webhook():
    """Process webhooks from providers or banking systems"""
    logger.info("Received webhook request")

    try:
        # Verify signature if provided
        signature = request.headers.get("X-Signature")
        if signature:
            if not verify_request_signature(request.data, signature):
                logger.warning("Invalid webhook signature")
                return jsonify({"error": "Invalid signature"}), 401

        # Process the webhook data
        webhook_data = request.json

        # Validate the webhook structure
        if not webhook_data or not isinstance(webhook_data, dict):
            logger.error("Invalid webhook data format")
            return jsonify({"error": "Invalid webhook data format"}), 400

        # Extract transaction ID from the webhook if available
        transaction_id = webhook_data.get("transaction_id")
        event_type = webhook_data.get("event_type")

        if not event_type:
            logger.error("Missing event_type in webhook data")
            return jsonify({"error": "Missing event_type in webhook data"}), 400

        # If this webhook is updating a transaction, find and update it
        if transaction_id:
            transaction = Transaction.query.filter_by(
                transaction_id=transaction_id
            ).first()

            if transaction:
                # Update transaction based on event type
                if event_type == "transaction_completed":
                    transaction.status = "completed"
                elif event_type == "transaction_failed":
                    transaction.status = "failed"
                    transaction.error_message = webhook_data.get(
                        "error_message", "No error details provided"
                    )
                elif event_type == "transaction_pending":
                    transaction.status = "pending"

                transaction.response_data = str(webhook_data)
                db.session.commit()
                logger.info(
                    f"Updated transaction {transaction_id} status to {transaction.status}"
                )

        # All webhook processing is considered successful even if transaction was not found
        # This prevents retries if the webhook is valid but our system doesn't have a record
        logger.info(f"Processed webhook: {event_type}")
        return (
            jsonify({"status": "success", "message": "Webhook processed successfully"}),
            200,
        )

    except Exception as e:
        logger.exception(f"Error processing webhook: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


@middleware_bp.route("/config", methods=["GET"])
@jwt_required()
def get_system_configurations():
    """Get all active system configurations"""
    current_user = get_jwt_identity()
    logger.info(f"Retrieving system configurations for user {current_user}")

    try:
        configs = SystemConfig.query.filter_by(is_active=True).all()

        results = [
            {
                "id": config.id,
                "system_name": config.system_name,
                "system_type": config.system_type,
                "base_url": config.base_url,
                "auth_type": config.auth_type,
                "is_active": config.is_active,
                "timeout": config.timeout,
                "retry_count": config.retry_count,
            }
            for config in configs
        ]

        logger.info(f"Retrieved {len(results)} system configurations")
        return jsonify({"configurations": results}), 200

    except Exception as e:
        logger.exception(f"Error retrieving system configurations: {str(e)}")
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
