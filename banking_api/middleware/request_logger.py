import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger("banking_api")


class RequestLoggerMiddleware(MiddlewareMixin):
    """
    Middleware to log details about each request including path, method, and timing.
    """

    def __init__(self, get_response=None):
        self.get_response = get_response
        super().__init__(get_response)

    def process_request(self, request):
        """Process the request and record start time"""
        request.start_time = time.time()

        # Log request details
        client_ip = self._get_client_ip(request)

        logger.info(
            f"Request received: {request.method} {request.path} | "
            f"IP: {client_ip} | "
            f"User: {request.user.username if hasattr(request, 'user') and request.user.is_authenticated else 'Anonymous'}"
        )

        return None

    def process_response(self, request, response):
        """Process the response and log timing information"""
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            status_code = response.status_code

            # Log response details
            logger.info(
                f"Response sent: {status_code} | "
                f"Duration: {duration:.4f}s | "
                f"Path: {request.method} {request.path}"
            )

            # Log response details at debug level if it's an error
            if status_code >= 400:
                logger.debug(
                    f"Error response details: {status_code} | "
                    f"Path: {request.method} {request.path}"
                )

        return response

    def _get_client_ip(self, request):
        """Get the client IP address from request headers"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Get the client IP from the X-Forwarded-For header
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            # Get the client IP from the REMOTE_ADDR header
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip
