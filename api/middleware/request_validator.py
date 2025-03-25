"""Request validation middleware using Marshmallow schemas."""

from functools import wraps
from typing import Callable, Any, Type, Optional, Dict
from flask import request
from marshmallow import Schema, ValidationError
from api.error_handlers import ValidationError as APIValidationError


def validate_request(
    schema: Type[Schema], location: str = "json", partial: bool = False
) -> Callable:
    """Decorator to validate incoming request data using a Marshmallow schema.

    Args:
        schema: Marshmallow schema class to use for validation
        location: Where to look for data ('json', 'form', 'args', 'files')
        partial: Whether to allow partial data validation

    Returns:
        Decorated function that validates request data

    Raises:
        APIValidationError: If validation fails

    Example:
        @app.route('/api/resource', methods=['POST'])
        @validate_request(ResourceSchema)
        def create_resource(validated_data):
            # validated_data is already validated
            return create_resource(validated_data)
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get request data based on location
            if location == "json":
                data = request.get_json()
            elif location == "form":
                data = request.form
            elif location == "args":
                data = request.args
            elif location == "files":
                data = request.files
            else:
                raise ValueError(f"Invalid location: {location}")

            try:
                # Validate data using schema
                schema_instance = schema()
                validated_data = schema_instance.load(data, partial=partial)

                # Add validated data to kwargs
                kwargs["validated_data"] = validated_data
                return fn(*args, **kwargs)

            except ValidationError as e:
                # Transform validation error into API error
                raise APIValidationError(
                    message="Invalid request data", details=e.messages
                )

        return wrapper

    return decorator


def validate_query_params(schema: Type[Schema], partial: bool = True) -> Callable:
    """Decorator to validate query parameters.

    This is a convenience wrapper around validate_request for query params.

    Args:
        schema: Marshmallow schema class to use for validation
        partial: Whether to allow partial validation (default True for query params)

    Returns:
        Decorated function that validates query parameters
    """
    return validate_request(schema, location="args", partial=partial)


def validate_files(schema: Type[Schema], partial: bool = False) -> Callable:
    """Decorator to validate file uploads.

    This is a convenience wrapper around validate_request for file uploads.

    Args:
        schema: Marshmallow schema class to use for validation
        partial: Whether to allow partial validation

    Returns:
        Decorated function that validates file uploads
    """
    return validate_request(schema, location="files", partial=partial)
