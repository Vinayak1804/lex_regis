from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.cases.models import Case
from apps.cases.models.master import CourtRoom, HearingType
from .master import HearingStatus

class Hearing(BaseModel):
    hearing_number = models.CharField(max_length=50, unique=True, db_index=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='hearings')
    
    hearing_type = models.ForeignKey(HearingType, on_delete=models.PROTECT)
    status = models.ForeignKey(HearingStatus, on_delete=models.PROTECT)
    court_room = models.ForeignKey(CourtRoom, on_delete=models.PROTECT, null=True, blank=True)
    presiding_judge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='presided_hearings')
    
    # Schedule
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    estimated_duration_minutes = models.PositiveIntegerField(default=30)
    
    # Actuals & Delay (ML Features)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    delay_minutes = models.IntegerField(default=0, help_text="Delay in starting (positive) or early start (negative)")
    
    # Outcome
    hearing_outcome = models.TextField(blank=True)
    
    # Media & Transcript Placeholders
    recording_url = models.URLField(max_length=500, blank=True)
    transcript_status = models.CharField(max_length=50, blank=True)
    
    # ML Features
    adjournment_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        indexes = [
            models.Index(fields=['hearing_number']),
            models.Index(fields=['case', 'scheduled_date']),
            models.Index(fields=['presiding_judge', 'scheduled_date']),
            models.Index(fields=['court_room', 'scheduled_date']),
        ]
        
    def __str__(self):
        return f"{self.hearing_number} - {self.case.case_number} on {self.scheduled_date}"
