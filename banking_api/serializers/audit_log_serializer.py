from rest_framework import serializers
from banking_api.models.audit_log import AuditLog
from banking_api.serializers.user_serializer import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    # Add a nested serializer for user
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        source="user",
        queryset=AuditLog.user.field.related_model.objects.all(),
        required=False,
        write_only=True,
        allow_null=True,
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "action",
            "resource_type",
            "resource_id",
            "user",
            "user_id",
            "details",
            "ip_address",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        """Additional validation for audit logs"""
        action = data.get("action")
        if action and action not in dict(AuditLog.ACTION_CHOICES):
            raise serializers.ValidationError(
                {
                    "action": "Invalid action. Must be one of: create, update, delete, login, logout, api_request."
                }
            )

        return data
