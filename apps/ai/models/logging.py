from django.db import models
from django.conf import settings

class AIRequestLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    endpoint = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    
    prompt = models.TextField()
    response = models.TextField(null=True, blank=True)
    
    status_code = models.IntegerField(null=True, blank=True)
    is_success = models.BooleanField(default=False)
    
    latency_ms = models.FloatField(null=True, blank=True)
    
    prompt_tokens = models.IntegerField(null=True, blank=True)
    completion_tokens = models.IntegerField(null=True, blank=True)
    total_tokens = models.IntegerField(null=True, blank=True)
    
    error_message = models.TextField(null=True, blank=True)
    traceback = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Request Log'
        verbose_name_plural = 'AI Request Logs'

    def __str__(self):
        return f"{self.endpoint} - {self.status_code} ({self.created_at})"
