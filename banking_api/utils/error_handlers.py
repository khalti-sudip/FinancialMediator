import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

logger = logging.getLogger('banking_api')

def custom_exception_handler(exc, context):
    """
    Custom exception handler for Django REST Framework
    
    Args:
        exc (Exception): The exception that occurred
        context (dict): The context for the exception
    
    Returns:
        Response: A custom response with error details
    """
    # First, get the standard error response
    response = exception_handler(exc, context)
    
    if response is None:
        # If no standard response, handle other exceptions
        if isinstance(exc, IntegrityError):
            data = {
                'error': 'Database integrity error',
                'detail': str(exc),
                'code': 'integrity_error'
            }
            response = Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, DjangoValidationError):
            data = {
                'error': 'Validation error',
                'detail': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'code': 'validation_error'
            }
            response = Response(data, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, Exception):
            # Generic exception handling
            logger.exception(f"Unhandled exception: {str(exc)}")
            data = {
                'error': 'Server error',
                'detail': str(exc) if not isinstance(exc, AssertionError) else 'Internal server error',
                'code': 'server_error'
            }
            response = Response(data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # For standard DRF exceptions, enhance the response
    else:
        # Extract the status code
        status_code = response.status_code
        
        # Get the existing data
        data = response.data
        
        # Add error code based on status code
        if 'code' not in data:
            if status_code == 400:
                data['code'] = 'bad_request'
            elif status_code == 401:
                data['code'] = 'unauthorized'
            elif status_code == 403:
                data['code'] = 'permission_denied'
            elif status_code == 404:
                data['code'] = 'not_found'
            elif status_code == 405:
                data['code'] = 'method_not_allowed'
            elif status_code == 429:
                data['code'] = 'throttled'
            else:
                data['code'] = 'error'
        
        # Add error wrapper if it's a validation error and not already wrapped
        if isinstance(exc, DRFValidationError) and 'error' not in data:
            response.data = {
                'error': 'Validation error',
                'detail': data,
                'code': 'validation_error'
            }
    
    return response