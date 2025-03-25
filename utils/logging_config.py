"""Enhanced logging configuration with structured JSON logs and request tracking."""

import os
import logging
import logging.handlers
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from flask import has_request_context, g, request
from pythonjsonlogger import jsonlogger
from api.middleware.request_tracking import request_id


class RequestInfoFilter(logging.Filter):
    """Filter to add request-specific information to log records.

    This filter enriches log records with request context when available,
    including request ID, IP address, URL, and HTTP method.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            if has_request_context():
                record.request_id = request_id
                record.remote_addr = request.remote_addr
                record.url = request.path
                record.method = request.method
                record.user_agent = request.headers.get("User-Agent", "unknown")
                record.referrer = request.referrer
            else:
                record.request_id = "no_request_id"
                record.remote_addr = "no_remote_addr"
                record.url = "no_url"
                record.method = "no_method"
                record.user_agent = "no_user_agent"
                record.referrer = "no_referrer"
        except Exception:
            # Fallback for when Flask is not available or other errors
            record.request_id = "logging_error"
            record.remote_addr = "logging_error"
            record.url = "logging_error"
            record.method = "logging_error"
            record.user_agent = "logging_error"
            record.referrer = "logging_error"

        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Enhanced JSON formatter for structured logging.

    This formatter creates detailed JSON log entries with additional
    metadata, timing information, and proper data masking.
    """

    def add_fields(
        self,
        log_record: Dict[str, Any],
        record: logging.LogRecord,
        message_dict: Dict[str, Any],
    ) -> None:
        """Add custom fields to the log record.

        Args:
            log_record: The log record being built
            record: The original logging record
            message_dict: Additional message information
        """
        super().add_fields(log_record, record, message_dict)

        # Add basic fields
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name

        # Add code location
        log_record["module"] = record.module
        log_record["function"] = record.funcName
        log_record["line"] = record.lineno

        # Add request context if available
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
            log_record["remote_addr"] = record.remote_addr
            log_record["url"] = record.url
            log_record["method"] = record.method
            log_record["user_agent"] = record.user_agent
            log_record["referrer"] = record.referrer

        # Add exception info if available
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        # Mask sensitive data
        self._mask_sensitive_data(log_record)

    def _mask_sensitive_data(self, log_record: Dict[str, Any]) -> None:
        """Mask sensitive data in log records.

        Args:
            log_record: The log record to mask
        """
        # Mask database URLs
        if isinstance(log_record.get("message"), str):
            log_record["message"] = self._mask_db_url(log_record["message"])

        # Mask sensitive headers
        if "headers" in log_record:
            headers = log_record["headers"]
            if "Authorization" in headers:
                headers["Authorization"] = "****"
            if "X-API-Key" in headers:
                headers["X-API-Key"] = "****"

    def _mask_db_url(self, message: str) -> str:
        """Mask sensitive information in database URLs.

        Args:
            message: The message containing potential database URLs

        Returns:
            Message with masked database URLs
        """
        import re

        # Mask PostgreSQL URLs
        message = re.sub(
            r"postgresql://[^:]+:[^@]+@", "postgresql://****:****@", message
        )
        # Mask Redis URLs
        message = re.sub(r"redis://[^:]+:[^@]+@", "redis://****:****@", message)
        return message


def configure_logging(log_level: Optional[str] = None) -> None:
    """Configure application logging with structured JSON output.

    Args:
        log_level: Optional logging level (DEBUG, INFO, etc.)
    """
    if log_level is None:
        log_level = os.environ.get("LOG_LEVEL", "INFO")

    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)

    # Create file handler
    log_file = os.environ.get("LOG_FILE", "logs/financial_mediator.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=10  # 10MB
    )
    file_handler.setLevel(numeric_level)

    # Create formatter
    formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")

    # Add request info filter
    request_filter = RequestInfoFilter()
    console_handler.addFilter(request_filter)
    file_handler.addFilter(request_filter)

    # Set formatter for handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Set Flask logger to use parent handlers
    flask_logger = logging.getLogger("flask.app")
    flask_logger.parent = root_logger
    flask_logger.propagate = True

    # Log startup message
    root_logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "log_file": log_file,
            "handlers": ["console", "file"],
        },
    )
