from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.common.choices.system import GenderChoices, LanguageChoices

class Profile(BaseModel):
    """
    Consolidated Profile for Personal, Contact, and Emergency Contact Information.
    Links to the User 1-to-1.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information (Tab 1)
    nationality = models.CharField(max_length=50, blank=True, null=True)
    languages_known = models.JSONField(default=list, blank=True, help_text="List of languages known")
    short_bio = models.TextField(blank=True, null=True)
    # Contact Information (Tab 4)
    client_type = models.CharField(max_length=50, blank=True, null=True, default='INDIVIDUAL')
    organization_name = models.CharField(max_length=255, blank=True, null=True)
    alternate_mobile = models.CharField(max_length=20, blank=True, null=True)
    office_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pin_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Emergency Contact (Tab 5)
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.email}"
