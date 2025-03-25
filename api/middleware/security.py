"""Security middleware for adding security headers and other protections."""

from functools import wraps
from typing import Callable, Any
from flask import make_response, request, current_app


def security_headers() -> Callable:
    """Decorator to add security headers to responses.

    Returns:
        Decorated function that adds security headers

    Example:
        @app.route('/api/resource')
        @security_headers()
        def get_resource():
            return {'data': 'resource'}
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            resp = make_response(f(*args, **kwargs))

            # Security headers
            resp.headers["X-Content-Type-Options"] = "nosniff"
            resp.headers["X-Frame-Options"] = "DENY"
            resp.headers["X-XSS-Protection"] = "1; mode=block"

            # Only add HSTS header if using HTTPS
            if request.is_secure or current_app.config.get("FORCE_HTTPS", False):
                resp.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )

            # Content Security Policy
            csp = current_app.config.get("CONTENT_SECURITY_POLICY")
            if csp:
                resp.headers["Content-Security-Policy"] = csp

            # Referrer Policy
            resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

            # Permissions Policy
            resp.headers["Permissions-Policy"] = (
                "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
                "magnetometer=(), microphone=(), payment=(), usb=()"
            )

            return resp

        return decorated_function

    return decorator


def configure_security(app: Any) -> None:
    """Configure security settings for the Flask application.

    Args:
        app: Flask application instance
    """
    # Enable Flask-Talisman if available
    try:
        from flask_talisman import Talisman

        Talisman(
            app,
            force_https=app.config.get("FORCE_HTTPS", False),
            strict_transport_security=True,
            strict_transport_security_max_age=31536000,
            strict_transport_security_include_subdomains=True,
            content_security_policy={
                "default-src": "'self'",
                "img-src": "'self' data: https:",
                "script-src": "'self'",
                "style-src": "'self' 'unsafe-inline'",
                "font-src": "'self' data:",
            },
        )
    except ImportError:
        app.logger.warning(
            "flask-talisman not installed. Using basic security headers only."
        )

    # Set session cookie settings
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        PERMANENT_SESSION_LIFETIME=1800,  # 30 minutes
    )

    # Configure CORS if available
    try:
        from flask_cors import CORS

        CORS(
            app,
            resources={
                r"/api/*": {
                    "origins": app.config.get("CORS_ORIGINS", []),
                    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                    "allow_headers": ["Content-Type", "Authorization"],
                    "expose_headers": ["X-Request-ID"],
                    "supports_credentials": True,
                }
            },
        )
    except ImportError:
        app.logger.warning("flask-cors not installed. CORS support disabled.")
