from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from banking_api.models.kyc import KYCProfile, DematAccount, Portfolio
from banking_api.serializers.kyc_serializer import (
    KYCProfileSerializer,
    DematAccountSerializer,
    PortfolioSerializer,
)


class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYCProfile.objects.all()
    serializer_class = KYCProfileSerializer

    @action(detail=True, methods=["post"])
    def verify(self, request, pk=None):
        profile = self.get_object()
        profile.is_verified = True
        profile.save()
        return Response({"status": "verified"})


class DematAccountViewSet(viewsets.ModelViewSet):
    queryset = DematAccount.objects.all()
    serializer_class = DematAccountSerializer

    @action(detail=True, methods=["post"])
    def renew(self, request, pk=None):
        account = self.get_object()
        # Add renewal logic here
        return Response({"status": "renewed"})


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.select_related("user").prefetch_related("transactions")
    serializer_class = PortfolioSerializer

    @action(detail=False, methods=["get"])
    @method_decorator(cache_page(60 * 5))  # Cache for 5 minutes
    def summary(self, request):
        portfolios = self.get_queryset()
        total_value = sum(
            p.quantity * p.current_price
            for p in portfolios.only("quantity", "current_price")
        )
        return Response(
            {
                "total_value": total_value,
                "positions": PortfolioSerializer(portfolios, many=True).data,
            }
        )
