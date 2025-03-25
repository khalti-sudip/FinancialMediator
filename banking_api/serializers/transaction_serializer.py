from rest_framework import serializers
from banking_api.models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_id",
            "source_system",
            "target_system",
            "transaction_type",
            "status",
            "amount",
            "currency",
            "user_id",
            "request_data",
            "response_data",
            "error_message",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        """Additional validation for transactions"""
        # Ensure transaction_id is unique if provided
        transaction_id = data.get("transaction_id")
        if (
            transaction_id
            and Transaction.objects.filter(transaction_id=transaction_id).exists()
        ):
            raise serializers.ValidationError(
                {"transaction_id": "Transaction with this ID already exists."}
            )

        # Validate amount if provided
        amount = data.get("amount")
        if amount is not None and amount <= 0:
            raise serializers.ValidationError(
                {"amount": "Amount must be greater than zero."}
            )

        return data
