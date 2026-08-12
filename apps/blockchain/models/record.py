from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class BlockchainRecord(BaseModel):
    RECORD_TYPES = (
        ('DOCUMENT_HASH', 'Document Hash'),
        ('CASE_EVENT', 'Case Event'),
        ('EVIDENCE_CHAIN', 'Evidence Chain of Custody'),
        ('AUDIT_TRAIL', 'Audit Trail'),
    )
    
    # Generic relation to link to Document, Case, Hearing etc
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    record_type = models.CharField(max_length=50, choices=RECORD_TYPES)
    
    # The actual data that was hashed
    data_payload = models.JSONField(help_text="The JSON representation of the data that was hashed")
    
    # Hashes and Blockchain Metadata
    sha256_hash = models.CharField(max_length=64, help_text="SHA-256 fingerprint of the payload")
    ipfs_cid = models.CharField(max_length=100, blank=True, help_text="IPFS Content Identifier")
    transaction_hash = models.CharField(max_length=100, blank=True, help_text="Ethereum Tx Hash")
    block_number = models.PositiveIntegerField(null=True, blank=True)
    
    # Verification details
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['sha256_hash']),
            models.Index(fields=['transaction_hash']),
        ]
        
    def __str__(self):
        return f"{self.get_record_type_display()} - {self.sha256_hash[:8]}..."
