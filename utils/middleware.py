import uuid
from functools import wraps
from flask import g, request, current_app
import logging
import time

logger = logging.getLogger(__name__)


def request_id_middleware():
    """
    Middleware to assign a unique ID to each request for tracking.
    This ID is stored in Flask's g object and can be accessed throughout the request.
    """

    def middleware(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate a unique request ID if one doesn't exist
            if not hasattr(g, "request_id"):
                g.request_id = str(uuid.uuid4())

            # Add the request ID to response headers
            response = f(*args, **kwargs)
            response.headers["X-Request-ID"] = g.request_id
            return response

        return decorated_function

    return middleware


def request_logger_middleware():
    """
    Middleware to log details about each request including path, method, and timing.
    """

    def middleware(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()

            # Log the request
            logger.info(f"Request started: {request.method} {request.path}")

            # Process the request
            response = f(*args, **kwargs)

            # Calculate and log the request duration
            duration = time.time() - start_time
            logger.info(
                f"Request completed: {request.method} {request.path} - "
                f"Status: {response.status_code} - Duration: {duration:.4f}s"
            )

            return response

        return decorated_function

    return middleware


def register_middleware(app):
    """
    Register all middleware with the Flask application.

    Args:
        app (Flask): The Flask application
    """

    @app.before_request
    def before_request():
        # Generate a unique request ID
        g.request_id = str(uuid.uuid4())
        g.start_time = time.time()

        # Log the start of the request
        logger.debug(
            f"Request started: {request.method} {request.path} [{g.request_id}]"
        )

    @app.after_request
    def after_request(response):
        # Add the request ID to the response headers
        response.headers["X-Request-ID"] = g.request_id

        # Calculate and log the request duration
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time
            logger.debug(
                f"Request completed: {request.method} {request.path} "
                f"[{g.request_id}] - Status: {response.status_code} - "
                f"Duration: {duration:.4f}s"
            )

        return response

    return app
