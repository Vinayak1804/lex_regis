from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.common.utilities.paths import get_organization_logo_path

class Organization(BaseModel):
    """
    Law Firm Profile.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organization_profile')
    
    firm_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=100, blank=True, null=True)
    gst_number = models.CharField(max_length=50, blank=True, null=True)
    logo = models.ImageField(upload_to=get_organization_logo_path, blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    practice_areas = models.JSONField(default=list, blank=True)
    number_of_lawyers = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.firm_name
