from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from .hearing import Hearing
from .master import AdjournmentReason

class Adjournment(BaseModel):
    hearing = models.ForeignKey(Hearing, on_delete=models.CASCADE, related_name='adjournments')
    reason = models.ForeignKey(AdjournmentReason, on_delete=models.PROTECT)
    
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requested_adjournments')
    requested_at = models.DateTimeField(auto_now_add=True)
    
    granted = models.BooleanField(default=False)
    granted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='granted_adjournments')
    
    new_scheduled_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['hearing']),
            models.Index(fields=['requested_by']),
        ]

    def __str__(self):
        return f"Adjournment for {self.hearing.hearing_number}"
