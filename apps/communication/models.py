from django.db import models
from django.conf import settings
from apps.cases.models.case import Case
from apps.accounts.models import Profile, ProfessionalProfile
from apps.documents.models.document import Document
from apps.common.models.base import BaseModel

class ConversationStatus(models.TextChoices):
    REQUESTED = 'REQUESTED', 'Requested'
    PENDING_ACCEPTANCE = 'PENDING_ACCEPTANCE', 'Pending Acceptance'
    ACTIVE = 'ACTIVE', 'Active'
    DECLINED = 'DECLINED', 'Declined'
    ARCHIVED = 'ARCHIVED', 'Archived'
    CLOSED = 'CLOSED', 'Closed'

class Conversation(models.Model):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='conversations', null=True, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    status = models.CharField(max_length=50, choices=ConversationStatus.choices, default=ConversationStatus.REQUESTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        if self.case:
            return f"Conversation for Case {self.case.case_number}"
        return f"Conversation {self.id}"

class MessageStatus(models.TextChoices):
    SENDING = 'SENDING', 'Sending'
    SENT = 'SENT', 'Sent'
    DELIVERED = 'DELIVERED', 'Delivered'
    READ = 'READ', 'Read'
    FAILED = 'FAILED', 'Failed'

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField(blank=True)
    attachment = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_messages')
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.SENT)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message {self.id} by {self.sender.email}"

class LawyerRequestStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    ACCEPTED = 'ACCEPTED', 'Accepted'
    DECLINED = 'DECLINED', 'Declined'
    CANCELLED = 'CANCELLED', 'Cancelled'
    EXPIRED = 'EXPIRED', 'Expired'

class LawyerRequest(BaseModel):
    client = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='lawyer_requests')
    lawyer = models.ForeignKey(ProfessionalProfile, on_delete=models.CASCADE, related_name='client_requests')
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='lawyer_requests', null=True, blank=True)
    
    initial_message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=LawyerRequestStatus.choices, default=LawyerRequestStatus.PENDING)
    
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Request from {self.client.user.email} to {self.lawyer.user.email}"
