"""Serializers for the providers app."""

from rest_framework import serializers
from .models import Provider, ProviderEndpoint, ProviderCredential


class ProviderEndpointSerializer(serializers.ModelSerializer):
    """Serializer for provider endpoints."""

    class Meta:
        """Meta options for ProviderEndpointSerializer."""

        model = ProviderEndpoint
        fields = [
            "id",
            "name",
            "path",
            "method",
            "requires_auth",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProviderCredentialSerializer(serializers.ModelSerializer):
    """Serializer for provider credentials."""

    class Meta:
        """Meta options for ProviderCredentialSerializer."""

        model = ProviderCredential
        fields = ["id", "key", "value", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {"value": {"write_only": True}}


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer for providers."""

    endpoints = ProviderEndpointSerializer(many=True, read_only=True)
    credentials = ProviderCredentialSerializer(many=True, read_only=True)

    class Meta:
        """Meta options for ProviderSerializer."""

        model = Provider
        fields = [
            "id",
            "name",
            "code",
            "api_key",
            "base_url",
            "status",
            "rate_limit",
            "created_at",
            "updated_at",
            "created_by",
            "endpoints",
            "credentials",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]
        extra_kwargs = {
            "api_key": {"write_only": True},
            "api_secret": {"write_only": True},
        }

    def create(self, validated_data):
        """Create a new provider."""
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
