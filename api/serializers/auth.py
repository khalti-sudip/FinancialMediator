"""
Authentication Serializers Module.

This module provides serializers for:
- JWT token issuance
- Token refresh
- Token verification
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
    TokenVerifySerializer,
)


class TokenObtainPairResponseSerializer(serializers.Serializer):
    """Response serializer for TokenObtainPairView."""
    
    access = serializers.CharField(help_text="JWT access token")
    refresh = serializers.CharField(help_text="JWT refresh token")

    class Meta:
        fields = ["access", "refresh"]


class TokenRefreshResponseSerializer(serializers.Serializer):
    """Response serializer for TokenRefreshView."""
    
    access = serializers.CharField(help_text="New JWT access token")

    class Meta:
        fields = ["access"]


class TokenVerifyResponseSerializer(serializers.Serializer):
    """Response serializer for TokenVerifyView."""
    
    # Empty response with 200 status indicates valid token
    pass
