"""Caching layer for API responses."""

from functools import wraps
from typing import Callable, Any, Optional, Union
from flask import request, current_app
from flask_caching import Cache
import hashlib
import json

# Initialize cache
cache = Cache()


def generate_cache_key(*args: Any, **kwargs: Any) -> str:
    """Generate a unique cache key from the arguments.

    Args:
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key

    Returns:
        A unique hash string for the cache key
    """
    # Create a dictionary of all arguments
    key_dict = {
        "args": args,
        "kwargs": kwargs,
        "path": request.path,
        "query_string": request.query_string.decode("utf-8"),
    }

    # Convert to a stable string representation
    key_str = json.dumps(key_dict, sort_keys=True)

    # Generate hash
    return hashlib.sha256(key_str.encode("utf-8")).hexdigest()


def cached(
    timeout: int = 300,
    key_prefix: str = "view",
    unless: Optional[Callable] = None,
    forced_update: Optional[Callable] = None,
) -> Callable:
    """Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache keys
        unless: Function that returns True if caching should be skipped
        forced_update: Function that returns True if cache should be updated

    Returns:
        Decorated function with caching

    Example:
        @app.route('/api/resource/<id>')
        @cached(timeout=300)
        def get_resource(id):
            return fetch_resource(id)
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args: Any, **kwargs: Any) -> Any:
            # Skip cache if unless returns True
            if unless and unless():
                return f(*args, **kwargs)

            # Generate cache key
            cache_key = f"{key_prefix}:{generate_cache_key(*args, **kwargs)}"

            # Get from cache
            rv = cache.get(cache_key)

            # Return cached value if exists and no forced update
            if rv is not None and not (forced_update and forced_update()):
                return rv

            # Generate new value
            rv = f(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, rv, timeout=timeout)

            return rv

        return decorated_function

    return decorator


def cache_invalidate(key_prefix: str, *args: Any, **kwargs: Any) -> None:
    """Invalidate a cached value.

    Args:
        key_prefix: Prefix of the cache key
        *args: Positional arguments used in the cache key
        **kwargs: Keyword arguments used in the cache key
    """
    cache_key = f"{key_prefix}:{generate_cache_key(*args, **kwargs)}"
    cache.delete(cache_key)


def cache_invalidate_pattern(pattern: str) -> None:
    """Invalidate all cache keys matching a pattern.

    Args:
        pattern: Pattern to match cache keys (e.g., 'view:user:*')
    """
    if hasattr(cache, "delete_pattern"):
        cache.delete_pattern(pattern)
    else:
        # Fallback for cache backends that don't support pattern deletion
        pass


def setup_cache(app: Any) -> None:
    """Initialize the cache with the application.

    Args:
        app: Flask application instance
    """
    config = {
        "CACHE_TYPE": app.config.get("CACHE_TYPE", "simple"),
        "CACHE_DEFAULT_TIMEOUT": app.config.get("CACHE_DEFAULT_TIMEOUT", 300),
    }

    # Add Redis config if using Redis cache
    if config["CACHE_TYPE"] == "redis":
        config.update(
            {
                "CACHE_REDIS_URL": app.config.get("REDIS_URL"),
                "CACHE_KEY_PREFIX": app.config.get("CACHE_KEY_PREFIX", "fm_cache:"),
            }
        )

    cache.init_app(app, config=config)
