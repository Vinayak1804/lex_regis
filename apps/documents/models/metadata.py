from django.db import models
from apps.common.models.base import BaseModel
from .document import Document

class DocumentMetadata(BaseModel):
    document = models.OneToOneField(Document, on_delete=models.CASCADE, related_name='metadata')
    pages = models.PositiveIntegerField(default=1)
    language = models.CharField(max_length=50, default='en')
    author = models.CharField(max_length=255, blank=True)
    creation_date = models.DateTimeField(null=True, blank=True)
    modification_date = models.DateTimeField(null=True, blank=True)
    keywords = models.CharField(max_length=500, blank=True)
    custom_metadata_json = models.JSONField(default=dict, blank=True)
    
    # AI and ML Placeholders
    ocr_language = models.CharField(max_length=50, blank=True)
    parser_version = models.CharField(max_length=50, blank=True)
    embedding_version = models.CharField(max_length=50, blank=True)
    summary_version = models.CharField(max_length=50, blank=True)
    extraction_version = models.CharField(max_length=50, blank=True)
    ai_provider = models.CharField(max_length=100, blank=True)
    extracted_text = models.TextField(blank=True, help_text="Text extracted via OCR or native parsing")
    def __str__(self):
        return f"Metadata for {self.document}"
