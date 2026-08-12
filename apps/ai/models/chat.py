from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.cases.models import Case
from apps.documents.models import Document

class Conversation(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_conversations')
    case = models.ForeignKey(Case, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_conversations')
    document = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_conversations')
    title = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Conversation {self.id} - {self.user.email}"


class Message(BaseModel):
    SENDER_CHOICES = (
        ('USER', 'User'),
        ('AI', 'AI Assistant'),
        ('SYSTEM', 'System'),
    )
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    token_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['created_at']
        
    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."
