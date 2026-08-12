from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.common.utilities.paths import get_document_upload_path
from apps.cases.models import Case
from apps.common.choices.system import DocumentFileTypeChoices, MimeTypeChoices, VerificationStatusChoices
from .master import DocumentType, DocumentCategory, DocumentStatus, DocumentVisibility
from .tag import DocumentTag

class Document(BaseModel):
    document_number = models.CharField(max_length=100, unique=True, db_index=True)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='documents')
    
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_documents')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='owned_documents')
    
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    category = models.ForeignKey(DocumentCategory, on_delete=models.PROTECT)
    status = models.ForeignKey(DocumentStatus, on_delete=models.PROTECT)
    visibility = models.ForeignKey(DocumentVisibility, on_delete=models.PROTECT)
    
    original_file = models.FileField(upload_to=get_document_upload_path)
    file_size = models.PositiveIntegerField(help_text="File size in bytes", default=0)
    file_extension = models.CharField(max_length=20, choices=DocumentFileTypeChoices.choices, blank=True)
    mime_type = models.CharField(max_length=100, choices=MimeTypeChoices.choices, blank=True)
    checksum = models.CharField(max_length=64, blank=True, help_text="SHA256 Checksum")
    storage_path = models.CharField(max_length=500, blank=True)
    
    upload_timestamp = models.DateTimeField(auto_now_add=True)
    version_number = models.PositiveIntegerField(default=1)
    
    description = models.TextField(blank=True)
    tags = models.ManyToManyField(DocumentTag, blank=True)
    is_confidential = models.BooleanField(default=False)
    
    ai_analysis_status = models.CharField(max_length=50, blank=True)
    ocr_status = models.CharField(max_length=50, blank=True)
    embedding_status = models.CharField(max_length=50, blank=True)
    summary_status = models.CharField(max_length=50, blank=True)
    
    blockchain_verification_status = models.CharField(max_length=50, choices=VerificationStatusChoices.choices, blank=True)
    blockchain_transaction_hash = models.CharField(max_length=100, blank=True)
    verification_timestamp = models.DateTimeField(null=True, blank=True)
    immutable_record_id = models.CharField(max_length=100, blank=True)
    
    signature_status = models.CharField(max_length=50, choices=VerificationStatusChoices.choices, blank=True)
    signer = models.CharField(max_length=255, blank=True)
    signed_timestamp = models.DateTimeField(null=True, blank=True)
    certificate_placeholder = models.TextField(blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['document_number']),
            models.Index(fields=['case', 'status']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"Doc {self.document_number}: {self.original_file.name}"
