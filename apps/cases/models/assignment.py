from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.accounts.models import ProfessionalProfile
from .case import Case

class CaseAssignment(BaseModel):
    ROLE_CHOICES = (
        ('PRIMARY', 'Primary Advocate'),
        ('ASSOCIATE', 'Associate Advocate'),
        ('JUNIOR', 'Junior Advocate'),
        ('ASSISTANT', 'Legal Assistant'),
        ('PARALEGAL', 'Paralegal'),
        ('MANAGER', 'Case Manager'),
    )
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='assignments')
    assigned_lawyer = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='case_assignments')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PRIMARY')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='assignments_made')
    assigned_on = models.DateTimeField(auto_now_add=True)
    assignment_notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Assignment: {self.assigned_lawyer} to {self.case}"
