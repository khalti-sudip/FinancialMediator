"""
Connection pool utility for managing external service requests.

This module provides a connection pool implementation that:
1. Manages connection pooling for external services
2. Implements request retries with exponential backoff
3. Handles timeouts and connection reuse
4. Provides thread-safe session management

The connection pool is implemented as a singleton to ensure consistent
connection management across the application.
"""

import requests
import threading
from typing import Optional, Dict, Any
import time
from django.conf import settings


class ConnectionPool:
    """
    Connection pool for external service requests.
    
    Provides:
    - Connection pooling
    - Request retries with exponential backoff
    - Timeout management
    - Connection reuse
    - Thread safety
    
    Usage:
    ```python
    # Get the singleton instance
    pool = ConnectionPool.get_instance()
    
    # Get a session
    session = pool.get_session()
    
    # Make a request
    response = pool.request(
        method="GET",
        url="https://api.example.com",
        params={"param": "value"},
        timeout=5
    )
    ```
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        """
        Initialize the connection pool.
        
        This constructor is protected and should not be called directly.
        Use get_instance() to get the singleton instance.
        """
        if not hasattr(self, 'session'):
            self.session = requests.Session()
            self._configure_session()
            
    @classmethod
    def get_instance(cls) -> 'ConnectionPool':
        """
        Get the singleton instance of the connection pool.
        
        Returns:
            ConnectionPool: Singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance
    
    def _configure_session(self) -> None:
        """
        Configure the requests session with default settings.
        
        Sets up:
        - Retry strategy
        - Timeout defaults
        - Connection pool size
        - Headers
        """
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=settings.POOL_CONNECTIONS,
            pool_maxsize=settings.POOL_MAXSIZE,
            max_retries=3,
            pool_block=True
        )
        
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.session.headers.update({
            'User-Agent': 'FinancialMediator/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_session(self) -> requests.Session:
        """
        Get the configured session.
        
        Returns:
            requests.Session: Configured session instance
        """
        return self.session
    
    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5
    ) -> requests.Response:
        """
        Make a request using the connection pool.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            params: Query parameters
            data: Request body data
            headers: Additional headers
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries
            backoff_factor: Backoff factor for retries
            
        Returns:
            requests.Response: Response object
            
        Raises:
            requests.exceptions.RequestException: If request fails after retries
        """
        session = self.get_session()
        
        for attempt in range(max_retries):
            try:
                response = session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=timeout
                )
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                
                # Exponential backoff
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
                
        raise requests.exceptions.RequestException("Request failed after retries")


def get_connection_pool() -> ConnectionPool:
    """Get the connection pool instance."""
    return ConnectionPool.get_instance()


def make_request(
    method: str,
    url: str,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
    max_retries: int = 3,
    backoff_factor: float = 0.5
) -> requests.Response:
    """
    Convenience function to make requests using the connection pool.
    
    Args:
        method: HTTP method
        url: Request URL
        params: Query parameters
        data: Request body data
        headers: Additional headers
        timeout: Request timeout in seconds
        max_retries: Maximum number of retries
        backoff_factor: Backoff factor for retries
        
    Returns:
        requests.Response: Response object
    """
    pool = get_connection_pool()
    return pool.request(method, url, params, data, headers, timeout, max_retries, backoff_factor)
