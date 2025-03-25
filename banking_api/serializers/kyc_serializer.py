from rest_framework import serializers
from banking_api.models.kyc import KYCProfile, DematAccount, Portfolio


class KYCProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCProfile
        fields = "__all__"
        read_only_fields = ["is_verified", "created_at", "updated_at"]


class DematAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = DematAccount
        fields = "__all__"
        read_only_fields = ["created_at"]


class PortfolioSerializer(serializers.ModelSerializer):
    profit_loss = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = "__all__"
        read_only_fields = ["current_price", "last_updated"]

    def get_profit_loss(self, obj):
        return (obj.current_price - obj.purchase_price) * obj.quantity
