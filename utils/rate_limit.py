"""
Rate limiting utilities for FinancialMediator.
"""

from typing import Dict, Any, Optional
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from datetime import datetime, timedelta
import time


class RateLimiter:
    """
    Rate limiter using Redis for distributed rate limiting.
    
    Implements sliding window algorithm for more accurate rate limiting.
    """
    
    def __init__(self):
        self.window_size = settings.RATE_LIMIT_WINDOW
        self.max_requests = settings.RATE_LIMIT_REQUESTS
        self.cache_prefix = "rate_limit"
    
    def _get_window_key(self, identifier: str, window: int) -> str:
        """Get cache key for a specific window."""
        return f"{self.cache_prefix}:{identifier}:{window}"
    
    def _get_current_window(self) -> int:
        """Get current window number."""
        return int(time.time() // self.window_size)
    
    def _cleanup_old_windows(self, identifier: str, current_window: int) -> None:
        """Clean up old windows from cache."""
        for window in range(current_window - 2, current_window):
            cache.delete(self._get_window_key(identifier, window))
    
    def check_limit(self, identifier: str) -> bool:
        """
        Check if the rate limit has been exceeded.
        
        Args:
            identifier: Unique identifier for rate limiting (e.g., IP, user ID)
            
        Returns:
            bool: True if within limit, False if exceeded
        """
        current_window = self._get_current_window()
        window_key = self._get_window_key(identifier, current_window)
        
        # Get current count
        count = cache.get(window_key, 0)
        
        # If within limit, increment and return True
        if count < self.max_requests:
            cache.incr(window_key, 1)
            cache.expire(window_key, self.window_size)
            self._cleanup_old_windows(identifier, current_window)
            return True
        
        # Check previous window for sliding window calculation
        prev_window_key = self._get_window_key(identifier, current_window - 1)
        prev_count = cache.get(prev_window_key, 0)
        
        # Calculate total requests in current sliding window
        total_requests = count + prev_count
        
        return total_requests < self.max_requests
    
    def get_remaining(self, identifier: str) -> int:
        """
        Get remaining requests in current window.
        
        Args:
            identifier: Unique identifier for rate limiting
            
        Returns:
            int: Number of remaining requests
        """
        current_window = self._get_current_window()
        window_key = self._get_window_key(identifier, current_window)
        
        count = cache.get(window_key, 0)
        return max(0, self.max_requests - count)
    
    def get_reset_time(self, identifier: str) -> float:
        """
        Get time until rate limit resets.
        
        Args:
            identifier: Unique identifier for rate limiting
            
        Returns:
            float: Seconds until reset
        """
        current_window = self._get_current_window()
        next_window = current_window + 1
        return (next_window * self.window_size) - time.time()


def rate_limit(
    identifier: str,
    window_size: int = 60,  # 1 minute default
    max_requests: int = 100
) -> Callable:
    """
    Decorator to apply rate limiting to a function.
    
    Args:
        identifier: Unique identifier for rate limiting
        window_size: Size of the rate limiting window in seconds
        max_requests: Maximum number of requests allowed in the window
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            limiter = RateLimiter()
            limiter.window_size = window_size
            limiter.max_requests = max_requests
            
            if not limiter.check_limit(identifier):
                raise RateLimitExceeded(
                    f"Rate limit exceeded. {limiter.get_remaining(identifier)} requests remaining."
                )
            
            return func(*args, **kwargs)
        
        return wrapper


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass
