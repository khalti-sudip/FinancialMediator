"""
FinancialMediator providers module.

This module contains the core provider system for FinancialMediator, including:
- Provider registration and management
- Request processing and routing
"""

from .utils import ProviderRegistry

__all__ = ['ProviderRegistry']
