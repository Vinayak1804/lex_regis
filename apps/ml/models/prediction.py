from django.db import models
from apps.common.models.base import BaseModel
from apps.cases.models import Case
from apps.cases.models.master import Court, CourtLevel

class CasePrediction(BaseModel):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='ml_prediction')
    
    # Predictions
    duration_days_predicted = models.PositiveIntegerField(help_text="Predicted case duration in days")
    success_probability = models.DecimalField(max_digits=5, decimal_places=2, help_text="Probability of winning (0-100%)")
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, help_text="Risk score (0-100)")
    delay_probability = models.DecimalField(max_digits=5, decimal_places=2, help_text="Probability of delays (0-100%)")
    
    # Model Metadata
    model_version = models.CharField(max_length=50)
    confidence_interval = models.CharField(max_length=50, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Prediction for {self.case.case_number}"

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
