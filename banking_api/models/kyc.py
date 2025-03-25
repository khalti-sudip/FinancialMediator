from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class KYCProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile_number = models.CharField(max_length=15, unique=True)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    document_type = models.CharField(max_length=50)
    document_number = models.CharField(max_length=50)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DematAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    boid = models.CharField(max_length=16, unique=True)
    status = models.CharField(max_length=20)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    demat = models.ForeignKey(DematAccount, on_delete=models.CASCADE)
    stock_symbol = models.CharField(max_length=20)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)
