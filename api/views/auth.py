"""
Authentication Views Module.

This module provides REST endpoints for user authentication:
- JWT token issuance
- Token refresh
- Token verification
"""

from rest_framework_simplejwt.views import (
    TokenObtainPairView as BaseTokenObtainPairView,
    TokenRefreshView as BaseTokenRefreshView,
    TokenVerifyView as BaseTokenVerifyView,
)
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiResponse

# Import token serializers
from api.serializers.auth import (
    TokenObtainPairResponseSerializer,
    TokenRefreshResponseSerializer,
    TokenVerifyResponseSerializer,
)


@extend_schema(
    responses={
        200: TokenObtainPairResponseSerializer,
        401: OpenApiResponse(description="Invalid credentials"),
    },
    description="Obtain JWT token pair for authentication",
)
class TokenObtainPairView(BaseTokenObtainPairView):
    """Custom token obtain pair view with enhanced documentation."""
    permission_classes = [AllowAny]


@extend_schema(
    responses={
        200: TokenRefreshResponseSerializer,
        401: OpenApiResponse(description="Invalid refresh token"),
    },
    description="Refresh access token using refresh token",
)
class TokenRefreshView(BaseTokenRefreshView):
    """Custom token refresh view with enhanced documentation."""
    permission_classes = [AllowAny]


@extend_schema(
    responses={
        200: TokenVerifyResponseSerializer,
        401: OpenApiResponse(description="Invalid token"),
    },
    description="Verify token validity",
)
class TokenVerifyView(BaseTokenVerifyView):
    """Custom token verify view with enhanced documentation."""
    permission_classes = [AllowAny]
