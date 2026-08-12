from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel

class JudgeSchedule(BaseModel):
    judge = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField()
    
    # 24-hour format availability
    start_time = models.TimeField(default='09:00:00')
    end_time = models.TimeField(default='17:00:00')
    
    is_available = models.BooleanField(default=True)
    leave_reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        unique_together = ('judge', 'date')
        indexes = [
            models.Index(fields=['judge', 'date']),
        ]

    def __str__(self):
        return f"{self.judge} schedule on {self.date}"
