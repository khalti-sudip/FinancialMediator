from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from banking_api.models.user import User
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.user_serializer import UserSerializer
from banking_api.services.user_service import UserService
from banking_api.exceptions import UserNotFoundError

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    
    This viewset handles all user-related operations using the UserService.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active", "role"]
    search_fields = ["username", "email"]
    ordering_fields = ["id", "username", "created_at"]
    ordering = ["-created_at"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()
    
    def get_permissions(self):
        """
        Override to ensure that only admins can list, create, update or delete users
        """
        if self.action in ["list", "create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super().get_permissions()
    
    def retrieve(self, request, *args, **kwargs):
        """
        Get user details
        
        Users can only view their own details unless they're an admin
        """
        try:
            instance = self.get_object()
            if request.user.id != instance.id and not request.user.is_staff:
                return Response(
                    {"error": "You do not have permission to access this user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except UserNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user
        """
        try:
            user = self.user_service.create_user(
                username=request.data["username"],
                email=request.data["email"],
                password=request.data["password"]
            )
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Update user information
        """
        try:
            instance = self.get_object()
            self.user_service.update_user(
                instance.id,
                **request.data
            )
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except UserNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a user
        """
        try:
            instance = self.get_object()
            self.user_service.delete_user(instance.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserNotFoundError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get current user details
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def _get_client_ip(self, request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def perform_create(self, serializer):
        """Create a new user and log the action"""
        user = serializer.save()

        # Log user creation
        AuditLog.log_action(
            action="create",
            resource_type="user",
            resource_id=str(user.id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_update(self, serializer):
        """Update a user and log the action"""
        user = serializer.save()

        # Log user update
        AuditLog.log_action(
            action="update",
            resource_type="user",
            resource_id=str(user.id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

    def perform_destroy(self, instance):
        """Delete a user and log the action"""
        user_id = instance.id

        # Log user deletion
        AuditLog.log_action(
            action="delete",
            resource_type="user",
            resource_id=str(user_id),
            user=self.request.user,
            ip_address=self._get_client_ip(self.request),
        )

        instance.delete()
