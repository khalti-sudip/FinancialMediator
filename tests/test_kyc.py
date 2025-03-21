
import pytest
from rest_framework.test import APIClient
from banking_api.models import KYC, User
from django.urls import reverse

@pytest.mark.django_db
class TestKYCIntegration:
    def test_kyc_creation_flow(self, client):
        # Test complete KYC flow
        user_data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
        user = User.objects.create_user(**user_data)
        
        kyc_data = {
            "full_name": "Test User",
            "mobile_number": "9876543210",
            "document_type": "citizenship",
            "document_number": "123456789"
        }
        
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.post(reverse('kyc-create'), kyc_data)
        
        assert response.status_code == 201
        assert KYC.objects.count() == 1
        assert KYC.objects.first().user == user
