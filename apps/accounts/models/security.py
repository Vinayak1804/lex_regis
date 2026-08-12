from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel

class SecuritySettings(BaseModel):
    """
    Security settings for a user.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='security_settings')
    
    two_factor_enabled = models.BooleanField(default=False)
    backup_email = models.EmailField(blank=True, null=True)
    backup_phone = models.CharField(max_length=20, blank=True, null=True)
    
    last_password_change = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Security Settings - {self.user.email}"
