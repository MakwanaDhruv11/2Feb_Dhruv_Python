from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    """
    Custom user model for the AI Job Agent.
    Allows for future extension of user profiles.
    """
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    is_email_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username


class OTPVerification(models.Model):
    """
    Holds temporary 6-digit OTP codes for email verification.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=20, default='register')

    class Meta:
        ordering = ['-created_at']

    @property
    def is_expired(self):
        # Expiry set to 10 minutes
        return timezone.now() - self.created_at > timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.username} - Code: {self.code}"
