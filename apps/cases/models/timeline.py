from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from .case import Case

class CaseTimeline(BaseModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='timeline')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    event_code = models.CharField(max_length=100, db_index=True)
    event_category = models.CharField(max_length=100, db_index=True)
    event_source = models.CharField(max_length=100, default='SYSTEM')
    
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['case', 'event_code']),
        ]

    def __str__(self):
        return f"Timeline {self.event_code} for {self.case}"
