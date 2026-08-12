from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.accounts.models import ProfessionalProfile

class LegalIssue(BaseModel):
    class UrgencyLevels(models.TextChoices):
        ROUTINE = 'ROUTINE', 'Routine'
        URGENT = 'URGENT', 'Urgent'
        EMERGENCY = 'EMERGENCY', 'Emergency'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='legal_issues')
    description = models.TextField()
    incident_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    people_involved = models.IntegerField(default=1)
    matter_value = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    urgency = models.CharField(max_length=20, choices=UrgencyLevels.choices, default=UrgencyLevels.ROUTINE)
    
    status = models.CharField(max_length=50, default='PENDING_ANALYSIS') # PENDING_ANALYSIS, ANALYZED, LAWYER_BOOKED

    def __str__(self):
        return f"Issue {self.id} by {self.user.email}"

class DocumentUpload(BaseModel):
    issue = models.ForeignKey(LegalIssue, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='intake_docs/%Y/%m/%d/')
    document_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Doc {self.id} for Issue {self.issue.id}"

class AIAnalysis(BaseModel):
    issue = models.OneToOneField(LegalIssue, on_delete=models.CASCADE, related_name='ai_analysis')
    category = models.CharField(max_length=100, blank=True)
    practice_area = models.CharField(max_length=100, blank=True)
    subcategory = models.CharField(max_length=100, blank=True)
    complexity = models.CharField(max_length=50, blank=True) # Low, Medium, High, Critical
    recommended_lawyer_type = models.CharField(max_length=100, blank=True)
    recommended_court = models.CharField(max_length=100, blank=True)
    
    # Text arrays / lists stored as JSON
    suggested_documents = models.JSONField(default=list)
    possible_acts = models.JSONField(default=list)
    possible_sections = models.JSONField(default=list)
    important_keywords = models.JSONField(default=list)
    suggested_next_steps = models.JSONField(default=list)
    
    timeline_estimate = models.CharField(max_length=100, blank=True)
    cost_estimate = models.CharField(max_length=100, blank=True)
    
    risk_level = models.IntegerField(default=50) # 0 to 100
    confidence_score = models.IntegerField(default=85) # 0 to 100

    def __str__(self):
        return f"Analysis for Issue {self.issue.id}"

class Recommendation(BaseModel):
    issue = models.ForeignKey(LegalIssue, on_delete=models.CASCADE, related_name='recommendations')
    lawyer = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE)
    match_score = models.IntegerField(default=0) # Match out of 100
    ranking_factors = models.JSONField(default=dict) # Details on why matched
    status = models.CharField(max_length=50, default='SUGGESTED') # SUGGESTED, BOOKED, REJECTED

    def __str__(self):
        return f"Rec {self.lawyer.user.get_full_name()} for Issue {self.issue.id}"

class SearchHistory(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    query_parameters = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Search by {self.user.email} at {self.timestamp}"

class ConsultationRequest(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        REJECTED = 'REJECTED', 'Rejected'
        INFO_REQUESTED = 'INFO_REQUESTED', 'Information Requested'

    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='consultation_requests')
    lawyer = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='incoming_consultations')
    issue = models.ForeignKey(LegalIssue, on_delete=models.CASCADE, related_name='consultations')
    
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    
    # Store snapshot data in case AI Analysis changes or gets deleted
    matter_category = models.CharField(max_length=100, blank=True)
    practice_area = models.CharField(max_length=100, blank=True)
    estimated_budget = models.CharField(max_length=100, blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Request {self.id} from {self.client.email} to {self.lawyer.user.email}"
