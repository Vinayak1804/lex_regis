from django.db import models
from apps.common.models.base import BaseModel

class DocumentTag(BaseModel):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name
