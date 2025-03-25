"""Health check endpoints for monitoring system status."""

from datetime import datetime
from typing import Dict, Any, Tuple
from flask import Blueprint, jsonify, current_app
from sqlalchemy import text
from redis.exceptions import RedisError

health_bp = Blueprint("health", __name__)


def check_database() -> Tuple[bool, str]:
    """Check database connectivity.

    Returns:
        Tuple of (is_healthy, message)
    """
    try:
        # Try a simple query
        current_app.db.session.execute(text("SELECT 1"))
        current_app.db.session.commit()
        return True, "Connected"
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {str(e)}")
        return False, str(e)


def check_redis() -> Tuple[bool, str]:
    """Check Redis connectivity.

    Returns:
        Tuple of (is_healthy, message)
    """
    try:
        redis_client = current_app.extensions.get("redis")
        if redis_client:
            redis_client.ping()
            return True, "Connected"
        return False, "Redis not configured"
    except RedisError as e:
        current_app.logger.error(f"Redis health check failed: {str(e)}")
        return False, str(e)


def check_celery() -> Tuple[bool, str]:
    """Check Celery worker status.

    Returns:
        Tuple of (is_healthy, message)
    """
    try:
        from api.tasks.celery_app import celery

        # Inspect active workers
        inspector = celery.control.inspect()
        active_workers = inspector.active()

        if active_workers:
            worker_count = len(active_workers)
            return True, f"{worker_count} workers active"
        return False, "No active workers"
    except Exception as e:
        current_app.logger.error(f"Celery health check failed: {str(e)}")
        return False, str(e)


@health_bp.route("/health")
def health_check() -> Tuple[Dict[str, Any], int]:
    """Health check endpoint.

    Returns:
        Tuple of (response_data, status_code)
    """
    # Check all components
    db_healthy, db_message = check_database()
    redis_healthy, redis_message = check_redis()
    celery_healthy, celery_message = check_celery()

    # Build response
    health_data = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": current_app.config.get("VERSION", "unknown"),
        "components": {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "message": db_message,
            },
            "redis": {
                "status": "healthy" if redis_healthy else "unhealthy",
                "message": redis_message,
            },
            "celery": {
                "status": "healthy" if celery_healthy else "unhealthy",
                "message": celery_message,
            },
        },
    }

    # Overall status is healthy only if all components are healthy
    if not all([db_healthy, redis_healthy, celery_healthy]):
        health_data["status"] = "unhealthy"

    # Add metrics if available
    try:
        from prometheus_client import REGISTRY

        metrics = {}
        for metric in REGISTRY.collect():
            for sample in metric.samples:
                metrics[sample.name] = sample.value
        health_data["metrics"] = metrics
    except Exception:
        current_app.logger.debug("Prometheus metrics not available")

    # Return 503 if unhealthy
    status_code = 200 if health_data["status"] == "healthy" else 503

    current_app.logger.info(
        "Health check completed",
        extra={
            "health_status": health_data["status"],
            "components": health_data["components"],
        },
    )

    return jsonify(health_data), status_code


@health_bp.route("/health/live")
def liveness() -> Tuple[Dict[str, str], int]:
    """Kubernetes liveness probe endpoint.

    This endpoint only checks if the application is running
    and can respond to HTTP requests.

    Returns:
        Tuple of (response_data, status_code)
    """
    return jsonify({"status": "alive"}), 200


@health_bp.route("/health/ready")
def readiness() -> Tuple[Dict[str, Any], int]:
    """Kubernetes readiness probe endpoint.

    This endpoint checks if the application is ready to
    handle requests by verifying all dependencies are available.

    Returns:
        Tuple of (response_data, status_code)
    """
    health_data, status_code = health_check()
    return health_data, status_code
