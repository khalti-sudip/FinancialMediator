"""Authentication and authorization decorators."""

from functools import wraps
from flask_jwt_extended import get_jwt
from api.error_handlers import AuthorizationError, AuthenticationError
from typing import List, Callable, Any


def require_role(roles: List[str]) -> Callable:
    """Decorator to check if the authenticated user has the required role.

    Args:
        roles: List of role names that are allowed to access the endpoint

    Returns:
        Decorated function that checks for role authorization

    Raises:
        AuthorizationError: If the user doesn't have the required role
        AuthenticationError: If no JWT token is present
    """

    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                claims = get_jwt()
            except Exception:
                raise AuthenticationError("No valid authentication token found")

            if "roles" not in claims or not any(
                role in claims["roles"] for role in roles
            ):
                raise AuthorizationError(
                    message="Insufficient permissions",
                    details={
                        "required_roles": roles,
                        "user_roles": claims.get("roles", []),
                    },
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def admin_required(fn: Callable) -> Callable:
    """Decorator to check if the authenticated user is an admin.

    This is a convenience decorator that wraps require_role(['admin']).

    Returns:
        Decorated function that checks for admin role
    """
    return require_role(["admin"])(fn)


def provider_access_required(fn: Callable) -> Callable:
    """Decorator to check if the authenticated user has provider access.

    This decorator checks for either admin or provider_manager roles.

    Returns:
        Decorated function that checks for provider access roles
    """
    return require_role(["admin", "provider_manager"])(fn)
