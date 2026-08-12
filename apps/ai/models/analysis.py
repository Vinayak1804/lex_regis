from django.db import models
from apps.common.models.base import BaseModel
from apps.documents.models import Document

class AIAnalysisResult(BaseModel):
    ANALYSIS_TYPES = (
        ('OCR', 'Optical Character Recognition'),
        ('SUMMARY', 'Document Summary'),
        ('CONTRACT_REVIEW', 'Contract Review'),
        ('CLAUSE_EXTRACTION', 'Clause Extraction'),
        ('LEGAL_RESEARCH', 'Legal Research'),
    )
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='ai_analyses')
    analysis_type = models.CharField(max_length=50, choices=ANALYSIS_TYPES)
    result_data = models.JSONField(default=dict)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, default='COMPLETED')
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.get_analysis_type_display()} for Doc {self.document.document_number}"
