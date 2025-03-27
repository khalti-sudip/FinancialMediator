"""Views for the providers app."""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Provider, ProviderKey, ProviderWebhook
from .serializers import (
    ProviderSerializer,
    ProviderKeySerializer,
    ProviderWebhookSerializer,
)
from .services.provider_service import ProviderService, ProviderKeyService, ProviderWebhookService
from banking_api.exceptions import ProviderError
from banking_api.utils.common import get_client_ip, get_user_agent

provider_service = ProviderService()
provider_key_service = ProviderKeyService()
provider_webhook_service = ProviderWebhookService()

class ProviderFilter(filters.FilterSet):
    """Filter set for Provider model."""

    status = filters.ChoiceFilter(choices=Provider._meta.get_field("status").choices)
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        """Meta options for ProviderFilter."""

        model = Provider
        fields = ["status", "created_after", "created_before"]

class ProviderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing providers.
    
    This viewset handles all provider operations using the ProviderService.
    """
    
    queryset = Provider.objects.all()
    serializer_class = ProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = ProviderFilter
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_service = ProviderService()
    
    def create(self, request, *args, **kwargs):
        """
        Create a new provider.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the created provider
        """
        try:
            provider = self.provider_service.create_provider(request.data)
            serializer = self.get_serializer(provider)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing provider.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the updated provider
        """
        try:
            provider = self.provider_service.update_provider(
                kwargs["pk"],
                request.data
            )
            serializer = self.get_serializer(provider)
            return Response(serializer.data)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a provider.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Empty response with 204 status
        """
        try:
            self.provider_service.delete_provider(kwargs["pk"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["get"])
    def get_by_name(self, request):
        """
        Get a provider by name.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the provider details
        """
        name = request.query_params.get("name")
        if not name:
            return Response(
                {"error": "name parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            provider = self.provider_service.get_provider_by_name(name)
            serializer = self.get_serializer(provider)
            return Response(serializer.data)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )

class ProviderKeyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing provider keys.
    
    This viewset handles all provider key operations using the ProviderKeyService.
    """
    
    queryset = ProviderKey.objects.all()
    serializer_class = ProviderKeySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_key_service = ProviderKeyService()
    
    def create(self, request, *args, **kwargs):
        """
        Create a new provider key.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the created key
        """
        try:
            key = self.provider_key_service.create_provider_key(
                request.data["provider_id"],
                request.data
            )
            serializer = self.get_serializer(key)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing provider key.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the updated key
        """
        try:
            key = self.provider_key_service.update_provider_key(
                kwargs["pk"],
                request.data
            )
            serializer = self.get_serializer(key)
            return Response(serializer.data)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a provider key.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Empty response with 204 status
        """
        try:
            self.provider_key_service.delete_provider_key(kwargs["pk"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProviderWebhookViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing provider webhooks.
    
    This viewset handles all webhook operations using the ProviderWebhookService.
    """
    
    queryset = ProviderWebhook.objects.all()
    serializer_class = ProviderWebhookSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provider_webhook_service = ProviderWebhookService()
    
    def create(self, request, *args, **kwargs):
        """
        Create a new webhook for a provider.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the created webhook
        """
        try:
            webhook = self.provider_webhook_service.create_webhook(
                request.data["provider_id"],
                request.data
            )
            serializer = self.get_serializer(webhook)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update an existing webhook.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response containing the updated webhook
        """
        try:
            webhook = self.provider_webhook_service.update_webhook(
                kwargs["pk"],
                request.data
            )
            serializer = self.get_serializer(webhook)
            return Response(serializer.data)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a webhook.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Empty response with 204 status
        """
        try:
            self.provider_webhook_service.delete_webhook(kwargs["pk"])
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProviderError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
