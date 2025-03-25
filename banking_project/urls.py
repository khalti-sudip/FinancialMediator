"""
URL configuration for banking_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from banking_api.views import (
    UserViewSet,
    TransactionViewSet,
    ApiKeyViewSet,
    SystemConfigViewSet,
    AuditLogViewSet,
    LoginView,
    RegisterView,
    VerifyTokenView,
    KYCViewSet,
    DematAccountViewSet,
    PortfolioViewSet,
)  # Added imports for new ViewSets
from banking_api.views.health_views import HealthCheckView
from banking_api.views.index_views import IndexView

# API Router
router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"transactions", TransactionViewSet)
router.register(r"api-keys", ApiKeyViewSet)
router.register(r"system-configs", SystemConfigViewSet)
router.register(r"audit-logs", AuditLogViewSet)
router.register(r"kyc", KYCViewSet)  # Added KYC endpoint
router.register(r"demat", DematAccountViewSet)  # Added Demat endpoint
router.register(r"portfolio", PortfolioViewSet)  # Added Portfolio endpoint

# URLs
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("admin/", admin.site.urls),
    # API Endpoints
    path("api/", include(router.urls)),
    # Authentication
    path("api/auth/login/", LoginView.as_view(), name="login"),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/verify/", VerifyTokenView.as_view(), name="token_verify"),
    # Health Check
    path("api/health/", HealthCheckView.as_view(), name="health_check"),
    path("health/", HealthCheckView.as_view(), name="health_check_alt"),
    # API Documentation and Browser
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
