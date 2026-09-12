from django.db import models
from django.conf import settings
from django.utils import timezone
import hashlib
import json

class SignatureRequestStatus(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING = 'PENDING', 'Pending'
    VIEWED = 'VIEWED', 'Viewed'
    PARTIALLY_SIGNED = 'PARTIALLY_SIGNED', 'Partially Signed'
    COMPLETED = 'COMPLETED', 'Completed'
    DECLINED = 'DECLINED', 'Declined'
    EXPIRED = 'EXPIRED', 'Expired'
    CANCELLED = 'CANCELLED', 'Cancelled'

class SignerStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VIEWED = 'VIEWED', 'Viewed'
    SIGNED = 'SIGNED', 'Signed'
    DECLINED = 'DECLINED', 'Declined'

class SignatureFieldType(models.TextChoices):
    SIGNATURE = 'SIGNATURE', 'Signature'
    INITIAL = 'INITIAL', 'Initial'
    DATE = 'DATE', 'Date'
    TEXT = 'TEXT', 'Text'
    CHECKBOX = 'CHECKBOX', 'Checkbox'

class SignatureEventTypes(models.TextChoices):
    REQUEST_CREATED = 'REQUEST_CREATED', 'Request Created'
    DOCUMENT_VIEWED = 'DOCUMENT_VIEWED', 'Document Viewed'
    SIGNER_AUTHENTICATED = 'SIGNER_AUTHENTICATED', 'Signer Authenticated'
    FIELD_COMPLETED = 'FIELD_COMPLETED', 'Field Completed'
    SIGNATURE_APPLIED = 'SIGNATURE_APPLIED', 'Signature Applied'
    REQUEST_DECLINED = 'REQUEST_DECLINED', 'Request Declined'
    REMINDER_SENT = 'REMINDER_SENT', 'Reminder Sent'
    REQUEST_CANCELLED = 'REQUEST_CANCELLED', 'Request Cancelled'
    REQUEST_EXPIRED = 'REQUEST_EXPIRED', 'Request Expired'
    SIGNING_COMPLETED = 'SIGNING_COMPLETED', 'Signing Completed'
    SIGNED_DOCUMENT_CREATED = 'SIGNED_DOCUMENT_CREATED', 'Signed Document Created'

class SignatureRequest(models.Model):
    document_version = models.ForeignKey('documents.DocumentVersion', on_delete=models.CASCADE, related_name='signature_requests')
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='requested_signatures')
    status = models.CharField(max_length=20, choices=SignatureRequestStatus.choices, default=SignatureRequestStatus.DRAFT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    signing_order_enabled = models.BooleanField(default=False)
    message = models.TextField(blank=True)

    def __str__(self):
        return f"SigReq for {self.document_version} - {self.status}"

class Signer(models.Model):
    signature_request = models.ForeignKey(SignatureRequest, on_delete=models.CASCADE, related_name='signers')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='signature_assignments')
    email = models.EmailField(blank=True) # Used if external signer
    
    role = models.CharField(max_length=100, blank=True)
    signing_order = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=SignerStatus.choices, default=SignerStatus.PENDING)
    
    viewed_at = models.DateTimeField(null=True, blank=True)
    authenticated_at = models.DateTimeField(null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['signing_order', 'id']

    def __str__(self):
        return f"Signer: {self.email or self.user} ({self.status})"

class SignatureField(models.Model):
    signature_request = models.ForeignKey(SignatureRequest, on_delete=models.CASCADE, related_name='fields')
    signer = models.ForeignKey(Signer, on_delete=models.CASCADE, related_name='fields')
    
    page = models.PositiveIntegerField(default=1)
    x = models.FloatField(default=0.0)
    y = models.FloatField(default=0.0)
    width = models.FloatField(default=100.0)
    height = models.FloatField(default=50.0)
    
    required = models.BooleanField(default=True)
    field_type = models.CharField(max_length=20, choices=SignatureFieldType.choices, default=SignatureFieldType.SIGNATURE)
    
    value = models.TextField(blank=True) # Stores the text, date, or signature reference

    def __str__(self):
        return f"{self.field_type} on Page {self.page} for {self.signer}"

class SignatureAuditEvent(models.Model):
    signature_request = models.ForeignKey(SignatureRequest, on_delete=models.CASCADE, related_name='audit_trail')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    signer = models.ForeignKey(Signer, on_delete=models.SET_NULL, null=True, blank=True)
    
    event_type = models.CharField(max_length=50, choices=SignatureEventTypes.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    auth_method = models.CharField(max_length=100, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    event_hash = models.CharField(max_length=64, blank=True)
    previous_event_hash = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ['timestamp', 'id']

    def save(self, *args, **kwargs):
        if not self.pk and not self.event_hash:
            # Calculate hash for immutability
            last_event = SignatureAuditEvent.objects.filter(signature_request=self.signature_request).last()
            prev_hash = last_event.event_hash if last_event else "genesis"
            
            data_to_hash = f"{self.signature_request.id}:{self.event_type}:{self.timestamp}:{prev_hash}:{json.dumps(self.metadata, sort_keys=True)}"
            self.previous_event_hash = prev_hash
            self.event_hash = hashlib.sha256(data_to_hash.encode('utf-8')).hexdigest()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"
