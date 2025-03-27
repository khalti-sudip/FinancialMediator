"""
FinancialMediator settings module.

This module imports the appropriate settings based on the environment.
"""

from .base import *

try:
    from .local import *
except ImportError:
    pass

try:
    from .production import *
except ImportError:
    pass
