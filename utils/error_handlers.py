import logging
import traceback
from flask import jsonify, request
from marshmallow.exceptions import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

# Configure logging
logger = logging.getLogger(__name__)


def handle_validation_error(error):
    """
    Handle Marshmallow validation errors

    Args:
        error (ValidationError): The validation error

    Returns:
        tuple: JSON response and status code
    """
    logger.warning(f"Validation error: {error.messages}")
    return jsonify({"error": "Validation error", "messages": error.messages}), 400


def handle_sqlalchemy_error(error):
    """
    Handle SQLAlchemy errors

    Args:
        error (SQLAlchemyError): The SQLAlchemy error

    Returns:
        tuple: JSON response and status code
    """
    logger.error(f"Database error: {str(error)}")
    return (
        jsonify(
            {
                "error": "Database error",
                "message": "An error occurred while accessing the database",
            }
        ),
        500,
    )


def handle_http_exception(error):
    """
    Handle HTTP exceptions

    Args:
        error (HTTPException): The HTTP exception

    Returns:
        tuple: JSON response and status code
    """
    logger.warning(f"HTTP exception: {error.description}, code: {error.code}")
    return jsonify({"error": error.name, "message": error.description}), error.code


def handle_generic_exception(error):
    """
    Handle all other exceptions

    Args:
        error (Exception): The exception

    Returns:
        tuple: JSON response and status code
    """
    # In production, you might want to be less verbose in the response
    logger.error(f"Unhandled exception: {str(error)}")
    logger.error(traceback.format_exc())

    return (
        jsonify(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred",
            }
        ),
        500,
    )


def register_error_handlers(app):
    """
    Register all error handlers with the Flask app

    Args:
        app (Flask): The Flask application
    """
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(SQLAlchemyError, handle_sqlalchemy_error)
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_generic_exception)

    logger.info("Error handlers registered")
