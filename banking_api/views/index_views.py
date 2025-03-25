import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest

logger = logging.getLogger("banking_api")


class IndexView(APIView):
    """API view for root endpoint"""

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Root endpoint to display API information
        Renders HTML template for browser requests,
        returns JSON response for API requests
        """
        # Check if the request wants JSON (API client)
        if "application/json" in request.headers.get("Accept", ""):
            api_info = {
                "name": "Banking Middleware API",
                "version": "1.0.0",
                "description": "Banking middleware API that connects financial service providers with banking applications",
                "endpoints": {
                    "api/": "API root with all available endpoints",
                    "api/health/": "Health check endpoint",
                    "api/auth/login/": "Authentication endpoint",
                    "api/auth/register/": "Registration endpoint",
                    "api/users/": "User management",
                    "api/transactions/": "Transaction management",
                    "api/api-keys/": "API key management",
                    "api/system-configs/": "System configuration management",
                },
                "documentation": "/api-auth/",
                "environment": "development" if settings.DEBUG else "production",
            }

            return Response(api_info, status=status.HTTP_200_OK)

        # Otherwise render the HTML template (browser)
        return render(
            request,
            "index.html",
            {
                "api_version": "1.0.0",
                "environment": "development" if settings.DEBUG else "production",
            },
        )
