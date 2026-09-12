from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.cases.models import Case

class HistoricalCaseFeature(BaseModel):
    """
    Stores extracted features and semantic embeddings for a historical case.
    Used for similarity retrieval and analytics.
    """
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='historical_features')
    
    # Structured Features
    jurisdiction = models.CharField(max_length=255, blank=True)
    court_level = models.CharField(max_length=100, blank=True)
    legal_issues = models.JSONField(default=list, blank=True)
    acts = models.JSONField(default=list, blank=True)
    sections = models.JSONField(default=list, blank=True)
    case_stage = models.CharField(max_length=100, blank=True)
    dispute_type = models.CharField(max_length=100, blank=True)
    relief_sought = models.TextField(blank=True)
    urgency = models.CharField(max_length=50, blank=True)
    complexity = models.CharField(max_length=50, blank=True)
    party_type = models.CharField(max_length=100, blank=True)
    document_types = models.JSONField(default=list, blank=True)
    
    # Outcomes / Metrics
    hearing_count = models.IntegerField(default=0)
    adjournment_count = models.IntegerField(default=0)
    duration_days = models.IntegerField(null=True, blank=True)
    disposition = models.CharField(max_length=255, blank=True)
    outcome_classification = models.CharField(max_length=100, blank=True) # Normalized
    
    # Data Quality
    QUALITY_CHOICES = (
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    )
    data_quality_score = models.CharField(max_length=20, choices=QUALITY_CHOICES, default='LOW')
    
    # Semantic Representation
    semantic_representation = models.TextField(blank=True, help_text="Text representation of the case for embedding")
    embedding = models.JSONField(null=True, blank=True, help_text="List of floats representing the dense vector")
    embedding_model_version = models.CharField(max_length=50, blank=True)
    index_version = models.CharField(max_length=50, blank=True)
    
    # Provenance
    is_synthetic = models.BooleanField(default=False, help_text="True if this is generated demo data")

    class Meta:
        db_table = 'ml_historical_case_features'


class HistoricalSearchLog(BaseModel):
    """
    Audit log of searches for historical cases.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='historical_searches')
    query_text = models.TextField(blank=True)
    # The new issue or case that triggered the search
    trigger_issue = models.ForeignKey('intake.LegalIssue', on_delete=models.SET_NULL, null=True, blank=True)
    trigger_case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, blank=True)
    
    results_count = models.IntegerField(default=0)
    model_version = models.CharField(max_length=50, blank=True)
    
    class Meta:
        db_table = 'ml_historical_search_logs'


class HistoricalSearchFeedback(BaseModel):
    """
    Feedback provided by lawyers on the retrieved historical cases.
    """
    search_log = models.ForeignKey(HistoricalSearchLog, on_delete=models.CASCADE, related_name='feedbacks')
    retrieved_case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='retrieval_feedbacks')
    
    FEEDBACK_CHOICES = (
        ('HIGHLY_RELEVANT', 'Highly Relevant'),
        ('RELEVANT', 'Relevant'),
        ('SOMEWHAT_RELEVANT', 'Somewhat Relevant'),
        ('NOT_RELEVANT', 'Not Relevant'),
        ('WRONG_CATEGORY', 'Wrong Category'),
    )
    feedback_type = models.CharField(max_length=50, choices=FEEDBACK_CHOICES)
    comments = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ml_historical_search_feedbacks'
