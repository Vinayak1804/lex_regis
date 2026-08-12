from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel

class ProfessionalProfile(BaseModel):
    """
    Professional and Education Information for Advocates.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='professional_profile')
    
    # Professional Information (Tab 2)
    bar_council_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    enrollment_date = models.DateField(blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    practice_areas = models.JSONField(default=list, blank=True, help_text="List of practice areas")
    law_firm = models.CharField(max_length=150, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    office_address = models.TextField(blank=True, null=True)
    professional_email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    
    # Education (Tab 3)
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    university = models.CharField(max_length=150, blank=True, null=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    certifications = models.JSONField(default=list, blank=True)
    specializations = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"Professional Profile - {self.user.email}"
