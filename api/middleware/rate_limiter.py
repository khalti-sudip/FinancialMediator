"""Rate limiting middleware for API endpoints."""

from functools import wraps
from typing import Callable, Any, Optional
from flask import request, current_app
from redis import Redis
from api.error_handlers import RateLimitError


class RateLimiter:
    """Rate limiter using Redis for request tracking.

    This class implements a sliding window rate limit using Redis
    for storing and tracking request counts.
    """

    def __init__(
        self,
        redis_url: str,
        limit: int = 100,
        window: int = 3600,
        key_prefix: str = "rate_limit",
    ):
        """Initialize the rate limiter.

        Args:
            redis_url: Redis connection URL
            limit: Maximum number of requests allowed in the window
            window: Time window in seconds
            key_prefix: Prefix for Redis keys
        """
        self.redis = Redis.from_url(redis_url)
        self.limit = limit
        self.window = window
        self.key_prefix = key_prefix

    def get_key(self, identifier: str) -> str:
        """Generate Redis key for the rate limit counter.

        Args:
            identifier: Unique identifier for the rate limit (e.g., IP address)

        Returns:
            Redis key string
        """
        return f"{self.key_prefix}:{identifier}"

    def is_rate_limited(self, identifier: str) -> bool:
        """Check if the identifier has exceeded the rate limit.

        Args:
            identifier: Unique identifier to check (e.g., IP address)

        Returns:
            True if rate limited, False otherwise
        """
        key = self.get_key(identifier)
        current = self.redis.get(key)

        if current is None:
            self.redis.setex(key, self.window, 1)
            return False

        if int(current) >= self.limit:
            return True

        self.redis.incr(key)
        return False

    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests allowed in the current window.

        Args:
            identifier: Unique identifier to check

        Returns:
            Number of remaining requests allowed
        """
        key = self.get_key(identifier)
        current = self.redis.get(key)
        if current is None:
            return self.limit
        return max(0, self.limit - int(current))


def rate_limit(
    limit: Optional[int] = None,
    window: Optional[int] = None,
    key_func: Optional[Callable] = None,
) -> Callable:
    """Decorator to apply rate limiting to a route.

    Args:
        limit: Override the default request limit
        window: Override the default time window
        key_func: Optional function to generate the rate limit key

    Returns:
        Decorated function with rate limiting

    Example:
        @app.route('/api/resource')
        @rate_limit(limit=100, window=3600)
        def get_resource():
            return {'data': 'resource'}
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Get rate limiter from app config or create new one
            limiter = current_app.config.get("RATE_LIMITER")
            if not limiter:
                redis_url = current_app.config["REDIS_URL"]
                limiter = RateLimiter(
                    redis_url=redis_url, limit=limit or 100, window=window or 3600
                )
                current_app.config["RATE_LIMITER"] = limiter

            # Get identifier for rate limiting
            if key_func:
                identifier = key_func()
            else:
                identifier = request.remote_addr

            # Check rate limit
            if limiter.is_rate_limited(identifier):
                remaining = limiter.get_remaining(identifier)
                reset_time = int(limiter.window)

                raise RateLimitError(
                    message="Rate limit exceeded",
                    details={
                        "limit": limiter.limit,
                        "remaining": remaining,
                        "reset": reset_time,
                    },
                )

            return fn(*args, **kwargs)

        return wrapper

    return decorator
