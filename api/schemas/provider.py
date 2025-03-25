"""Schema definitions for Provider model serialization and validation."""

from marshmallow import Schema, fields, validate, post_load
from typing import Dict, Any


class ProviderSchema(Schema):
    """Schema for serializing and deserializing Provider models.

    This schema handles validation of provider data and provides proper error messages.
    It also ensures that sensitive data like API secrets are not exposed in responses.
    """

    # Read-only fields
    id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Required fields
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Provider name is required"},
    )
    api_key = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=256),
        error_messages={"required": "API key is required"},
    )
    provider_type = fields.Str(
        required=True,
        validate=validate.OneOf(["payment", "kyc", "banking"]),
        error_messages={
            "required": "Provider type is required",
            "validator_failed": "Provider type must be one of: payment, kyc, banking",
        },
    )
    base_url = fields.Url(
        required=True,
        validate=validate.Length(max=256),
        error_messages={
            "required": "Base URL is required",
            "invalid": "Invalid URL format",
        },
    )

    # Optional fields
    api_secret = fields.Str(
        validate=validate.Length(max=256), load_only=True  # Never include in response
    )
    status = fields.Str(
        validate=validate.OneOf(["active", "inactive", "suspended"]),
        dump_default="active",
        error_messages={
            "validator_failed": "Status must be one of: active, inactive, suspended"
        },
    )
    webhook_url = fields.Url(
        validate=validate.Length(max=256),
        allow_none=True,
        error_messages={"invalid": "Invalid webhook URL format"},
    )

    @post_load
    def process_data(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Process the data after validation.

        This method can be used to transform or clean the data before it's used
        to create or update a Provider model.

        Args:
            data: The validated data dictionary
            **kwargs: Additional arguments passed by marshmallow

        Returns:
            The processed data dictionary
        """
        # Convert URLs to strings if they're URL objects
        if "base_url" in data and hasattr(data["base_url"], "geturl"):
            data["base_url"] = data["base_url"].geturl()
        if "webhook_url" in data and hasattr(data["webhook_url"], "geturl"):
            data["webhook_url"] = data["webhook_url"].geturl()

        return data
