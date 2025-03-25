"""URL Configuration for the Banking app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.account import BankAccountViewSet
from .views.payment import PaymentMethodViewSet, PaymentViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'accounts', BankAccountViewSet, basename='account')
router.register(r'payment-methods', PaymentMethodViewSet, basename='payment-method')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
]
