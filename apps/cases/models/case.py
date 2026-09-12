from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.accounts.models import Profile, ProfessionalProfile, Organization
import uuid

class CaseStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    AI_ANALYSED = 'AI_ANALYSED', 'AI Analysed'
    PENDING_ACCEPTANCE = 'PENDING_ACCEPTANCE', 'Pending Lawyer Acceptance'
    LAWYER_ASSIGNED = 'LAWYER_ASSIGNED', 'Lawyer Assigned'
    CONSULTATION = 'CONSULTATION', 'Consultation Scheduled'
    EVIDENCE = 'EVIDENCE', 'Evidence Collection'
    LEGAL_NOTICE = 'LEGAL_NOTICE', 'Legal Notice'
    PETITION = 'PETITION', 'Petition Drafting'
    FILED = 'FILED', 'Case Filed'
    HEARINGS = 'HEARINGS', 'Hearings'
    JUDGEMENT = 'JUDGEMENT', 'Judgement Reserved'
    CLOSED = 'CLOSED', 'Closed'
    ARCHIVED = 'ARCHIVED', 'Archived'
    LAWYER_DECLINED = 'LAWYER_DECLINED', 'Lawyer Declined'

class MatterSource(models.TextChoices):
    AI_INTAKE = 'AI_INTAKE', 'AI Intake'
    TALK_TO_LAWYER = 'TALK_TO_LAWYER', 'Talk to a Lawyer'
    MANUAL = 'MANUAL', 'Manual Case Creation'

class Case(BaseModel):
    # Core Information
    case_number = models.CharField(max_length=50, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    ai_summary = models.TextField(blank=True)
    
    # Relationships
    client = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name='cases')
    assigned_lawyer = models.ForeignKey(ProfessionalProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_cases')
    assigned_law_firm = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, related_name='firm_cases')
    
    # Classification
    matter_category = models.CharField(max_length=100, blank=True)
    practice_area = models.CharField(max_length=100, blank=True)
    sub_category = models.CharField(max_length=100, blank=True)
    complexity = models.CharField(max_length=50, blank=True)
    risk_level = models.CharField(max_length=50, blank=True)
    
    # Estimates
    timeline_estimate = models.CharField(max_length=100, blank=True)
    budget_estimate = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    case_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    
    # Attributes
    priority = models.CharField(max_length=50, blank=True)
    court = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    # State & Source
    status = models.CharField(max_length=50, choices=CaseStatus.choices, default=CaseStatus.DRAFT)
    matter_source = models.CharField(max_length=20, choices=MatterSource.choices, default=MatterSource.MANUAL)
    ai_confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Reference
    ai_analysis_id = models.UUIDField(null=True, blank=True)
    
    # Legacy / Other useful tracking
    opponent_name = models.CharField(max_length=255, blank=True)
    incident_date = models.DateField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['case_number']),
            models.Index(fields=['status']),
            models.Index(fields=['assigned_lawyer']),
            models.Index(fields=['client']),
        ]

    def __str__(self):
        return f"{self.case_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.case_number:
            self.case_number = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
