"""
Connection pooling utilities for FinancialMediator.
"""

from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import threading
from django.conf import settings


class ConnectionPool:
    """
    Connection pool for external service requests.
    
    Provides:
    - Connection pooling
    - Request retries with exponential backoff
    - Timeout management
    - Connection reuse
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'session'):
            self.session = requests.Session()
            self._configure_session()
    
    def _configure_session(self):
        """Configure the requests session."""
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        # Configure adapter
        adapter = HTTPAdapter(
            pool_connections=settings.POOL_CONNECTIONS,
            pool_maxsize=settings.POOL_MAXSIZE,
            max_retries=retry_strategy
        )
        
        # Mount adapter
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get_session(self) -> requests.Session:
        """Get the configured session."""
        return self.session
    
    def make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: int = 30
    ) -> requests.Response:
        """
        Make a request using the connection pool.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            headers: Request headers
            data: Request data
            timeout: Request timeout in seconds
            
        Returns:
            requests.Response: Response object
        """
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                json=data if method in ['POST', 'PUT'] else None,
                data=data if method in ['GET', 'DELETE'] else None,
                timeout=timeout
            )
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise e


def get_connection_pool() -> ConnectionPool:
    """Get the connection pool instance."""
    return ConnectionPool()


def make_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> requests.Response:
    """
    Convenience function to make requests using the connection pool.
    
    Args:
        method: HTTP method
        url: Request URL
        headers: Request headers
        data: Request data
        timeout: Request timeout in seconds
        
    Returns:
        requests.Response: Response object
    """
    pool = get_connection_pool()
    return pool.make_request(method, url, headers, data, timeout)
