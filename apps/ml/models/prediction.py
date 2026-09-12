from django.db import models
from apps.common.models.base import BaseModel
from apps.cases.models import Case
from apps.cases.models.master import Court
from apps.accounts.models import ProfessionalProfile
from .registry import ModelVersion

class BasePrediction(BaseModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    model_version = models.ForeignKey(ModelVersion, on_delete=models.SET_NULL, null=True, blank=True)
    confidence = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    explanation = models.TextField(blank=True)
    
    class Meta:
        abstract = True

class UrgencyPrediction(BasePrediction):
    URGENCY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical')
    )
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES)
    probability = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"Urgency: {self.urgency_level} for {self.case.case_number}"

class ComplexityPrediction(BasePrediction):
    COMPLEXITY_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    )
    complexity_level = models.CharField(max_length=20, choices=COMPLEXITY_CHOICES)
    probability = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Complexity: {self.complexity_level} for {self.case.case_number}"

class DurationPrediction(BasePrediction):
    median_days = models.PositiveIntegerField()
    lower_bound_days = models.PositiveIntegerField(null=True, blank=True)
    upper_bound_days = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Duration: {self.median_days} days for {self.case.case_number}"

class FeePrediction(BasePrediction):
    median_fee = models.DecimalField(max_digits=14, decimal_places=2)
    lower_bound_fee = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    upper_bound_fee = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Fee: {self.median_fee} for {self.case.case_number}"

class AdjournmentRiskPrediction(BasePrediction):
    RISK_CHOICES = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    )
    risk_level = models.CharField(max_length=20, choices=RISK_CHOICES)
    probability = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Adjournment Risk: {self.risk_level} for {self.case.case_number}"

class LawyerMatchPrediction(BasePrediction):
    lawyer = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE)
    match_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="0-100")
    
    def __str__(self):
        return f"Match: {self.lawyer} for {self.case.case_number} ({self.match_score}%)"

class CourtWorkload(BaseModel):
    court = models.OneToOneField(Court, on_delete=models.CASCADE, related_name='workload_stats')
    
    active_cases = models.PositiveIntegerField(default=0)
    pending_cases = models.PositiveIntegerField(default=0)
    average_disposal_time_days = models.PositiveIntegerField(default=0)
    
    congestion_index = models.DecimalField(max_digits=5, decimal_places=2, help_text="0 (Empty) to 100 (Extremely congested)")
    
    class Meta:
        ordering = ['-congestion_index']
        
    def __str__(self):
        return f"{self.court.name} - Congestion: {self.congestion_index}"
