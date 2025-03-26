"""
Financial Mediator Providers Module.

This module provides a modular system for managing:
- Financial institutions (banks, wallets, etc.)
- Financial providers (payment gateways, KYC services, etc.)
- Request processing and routing
"""

from .utils.registry import registry

__all__ = ['registry']
