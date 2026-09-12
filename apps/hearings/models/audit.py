from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.cases.models import Case
from .hearing import Hearing

class HearingActionChoices(models.TextChoices):
    CREATED = 'CREATED', 'Created'
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    RESCHEDULED = 'RESCHEDULED', 'Rescheduled'
    ADJOURNED = 'ADJOURNED', 'Adjourned'
    POSTPONED = 'POSTPONED', 'Postponed'
    CANCELLED = 'CANCELLED', 'Cancelled'
    COMPLETED = 'COMPLETED', 'Completed'

class HearingAuditLog(BaseModel):
    hearing = models.ForeignKey(Hearing, on_delete=models.CASCADE, related_name='audit_logs')
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='hearing_audit_logs')
    
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hearing_actions')
    action = models.CharField(max_length=50, choices=HearingActionChoices.choices)
    
    # Track what changed
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField(null=True, blank=True)
    
    reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hearing', 'created_at']),
            models.Index(fields=['case', 'created_at']),
        ]
        
    def __str__(self):
        return f"{self.action} on {self.hearing.hearing_number} by {self.actor}"
