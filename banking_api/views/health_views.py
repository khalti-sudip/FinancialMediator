import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.db import connection
from django.conf import settings

logger = logging.getLogger("banking_api")


class HealthCheckView(APIView):
    """API view for health check endpoint"""

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Basic health check endpoint for monitoring
        """
        # Check database connection
        db_status = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = cursor.fetchone()[0] == 1
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")

        # Build health status response
        health_status = {
            "status": "healthy" if db_status else "unhealthy",
            "database_connected": db_status,
            "api_version": "1.0.0",
            "environment": "development" if settings.DEBUG else "production",
        }

        status_code = (
            status.HTTP_200_OK if db_status else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return Response(health_status, status=status_code)
