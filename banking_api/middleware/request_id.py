import uuid
import logging
from django.utils.deprecation import MiddlewareMixin
from banking_api.utils.logging_config import set_current_request

logger = logging.getLogger("banking_api")


class RequestIdMiddleware(MiddlewareMixin):
    """
    Middleware to assign a unique ID to each request for tracking.
    This ID is attached to the request object and can be accessed throughout the request.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """Process the request and attach a unique ID"""
        request_id = str(uuid.uuid4())
        request.request_id = request_id

        # Store request in thread local for logging
        set_current_request(request)

        logger.debug(f"Request ID assigned: {request_id}")
        return None

    def process_response(self, request, response):
        """Add request ID to response headers"""
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id

        # Clear the thread local request at the end of the request
        set_current_request(None)

        return response
