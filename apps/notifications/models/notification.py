from django.db import models
from apps.common.models.base import BaseModel
from apps.accounts.models import User

class NotificationType(models.TextChoices):
    SYSTEM = 'SYSTEM', 'System Alert'
    CASE = 'CASE', 'Case Update'
    HEARING = 'HEARING', 'Hearing Reminder'
    DOCUMENT = 'DOCUMENT', 'Document Upload'
    AI = 'AI', 'AI Analysis'
    BLOCKCHAIN = 'BLOCKCHAIN', 'Blockchain Verification'
    LAWYER_ASSIGNMENT = 'LAWYER_ASSIGNMENT', 'Lawyer Assignment'
    MESSAGE = 'MESSAGE', 'Message'

class Notification(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices, default=NotificationType.SYSTEM)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Generic relation to target object (e.g. Case, Hearing, Document)
    # Keeping it simple with target_url for now
    target_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.title}"
