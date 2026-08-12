from django.db import models
from apps.common.models.base import BaseModel
from .master import CaseType, CaseCategory

class MatterTemplate(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    
    # Defaults
    case_type = models.ForeignKey(CaseType, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(CaseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    practice_area = models.CharField(max_length=100, blank=True)
    
    # Checklists and Suggestions
    suggested_acts = models.JSONField(default=list, blank=True)
    suggested_sections = models.JSONField(default=list, blank=True)
    required_documents = models.JSONField(default=list, blank=True)
    checklist = models.JSONField(default=list, blank=True)
    recommended_workflow = models.JSONField(default=list, blank=True)
    default_tasks = models.JSONField(default=list, blank=True)
    required_parties = models.JSONField(default=list, blank=True)
    
    # Metadata
    risk_level = models.CharField(max_length=50, blank=True)
    priority = models.CharField(max_length=50, blank=True)
    estimated_duration_days = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
