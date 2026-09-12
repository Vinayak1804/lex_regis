from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.cases.models import Case

class PredictionFeedback(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='prediction_feedback')
    
    # Which prediction we are giving feedback on
    PREDICTION_TYPES = (
        ('URGENCY', 'Urgency'),
        ('COMPLEXITY', 'Complexity'),
        ('DURATION', 'Duration'),
        ('FEE_RANGE', 'Fee Range'),
        ('ADJOURNMENT', 'Adjournment Risk'),
        ('LAWYER_MATCH', 'Lawyer Match'),
    )
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPES)
    
    # The feedback
    FEEDBACK_CHOICES = (
        ('HELPFUL', 'Helpful'),
        ('INCORRECT', 'Incorrect'),
        ('UNCERTAIN', 'Uncertain'),
    )
    feedback = models.CharField(max_length=20, choices=FEEDBACK_CHOICES)
    
    # Optional corrections
    corrected_value = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    
    # What version produced this prediction?
    model_version = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.prediction_type} - {self.feedback} for {self.case.case_number}"
