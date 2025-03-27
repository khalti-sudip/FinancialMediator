from django.urls import path
from .views import HealthCheckView, DatabaseHealthView, CacheHealthView, CeleryHealthView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/db/', DatabaseHealthView.as_view(), name='database-health'),
    path('health/cache/', CacheHealthView.as_view(), name='cache-health'),
    path('health/celery/', CeleryHealthView.as_view(), name='celery-health'),
]
