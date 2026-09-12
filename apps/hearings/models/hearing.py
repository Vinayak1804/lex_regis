from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.cases.models import Case
from apps.cases.models.master import CourtRoom

class HearingStatus(models.TextChoices):
    SCHEDULED = 'SCHEDULED', 'Scheduled'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    ADJOURNED = 'ADJOURNED', 'Adjourned'
    POSTPONED = 'POSTPONED', 'Postponed'
    CANCELLED = 'CANCELLED', 'Cancelled'

class HearingMode(models.TextChoices):
    PHYSICAL = 'PHYSICAL', 'Physical'
    VIRTUAL = 'VIRTUAL', 'Virtual'
    HYBRID = 'HYBRID', 'Hybrid'

class HearingPriority(models.TextChoices):
    LOW = 'LOW', 'Low'
    NORMAL = 'NORMAL', 'Normal'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'

class HearingTypeChoices(models.TextChoices):
    FIRST_HEARING = 'FIRST_HEARING', 'First Hearing'
    ADMISSION = 'ADMISSION', 'Admission'
    ARGUMENTS = 'ARGUMENTS', 'Arguments'
    EVIDENCE = 'EVIDENCE', 'Evidence'
    CROSS_EXAMINATION = 'CROSS_EXAMINATION', 'Cross Examination'
    FINAL_ARGUMENTS = 'FINAL_ARGUMENTS', 'Final Arguments'
    JUDGMENT = 'JUDGMENT', 'Judgment'
    BAIL_HEARING = 'BAIL_HEARING', 'Bail Hearing'
    INTERIM_APPLICATION = 'INTERIM_APPLICATION', 'Interim Application'
    MENTIONING = 'MENTIONING', 'Mentioning'
    MEDIATION = 'MEDIATION', 'Mediation'
    CONCILIATION = 'CONCILIATION', 'Conciliation'
    OTHER = 'OTHER', 'Other'

class Hearing(BaseModel):
    hearing_number = models.CharField(max_length=50, unique=True, db_index=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='hearings')
    
    title = models.CharField(max_length=255, blank=True)
    
    hearing_type = models.CharField(max_length=50, choices=HearingTypeChoices.choices, default=HearingTypeChoices.FIRST_HEARING)
    status = models.CharField(max_length=50, choices=HearingStatus.choices, default=HearingStatus.SCHEDULED)
    mode = models.CharField(max_length=20, choices=HearingMode.choices, default=HearingMode.PHYSICAL)
    priority = models.CharField(max_length=20, choices=HearingPriority.choices, default=HearingPriority.NORMAL)
    
    court_room = models.ForeignKey(CourtRoom, on_delete=models.PROTECT, null=True, blank=True)
    presiding_judge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='presided_hearings')
    
    # Canonical DateTime fields
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=timezone.now)
    
    notes = models.TextField(blank=True)
    next_action = models.TextField(blank=True)
    next_hearing_date = models.DateField(null=True, blank=True)
    
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
            models.Index(fields=['case', 'start_time']),
            models.Index(fields=['presiding_judge', 'start_time']),
            models.Index(fields=['court_room', 'start_time']),
        ]
        
    def __str__(self):
        return f"{self.hearing_number} - {self.case.case_number}"
