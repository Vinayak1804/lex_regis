from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from django.utils import timezone
import datetime

class Verification(BaseModel):
    """
    Verification model for OTPs.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='verifications')
    
    VERIFICATION_TYPES = (
        ('EMAIL', 'Email Verification'),
        ('MOBILE', 'Mobile Verification'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('TWO_FACTOR', 'Two-Factor Authentication'),
    )
    
    verification_type = models.CharField(max_length=20, choices=VERIFICATION_TYPES)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    def is_valid(self):
        return not self.is_verified and self.expires_at > timezone.now()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + datetime.timedelta(minutes=15)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_verification_type_display()} for {self.user.email}"
