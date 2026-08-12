from django.db import models
from apps.common.models.base import BaseModel

class MasterEntity(BaseModel):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class DocumentType(MasterEntity): pass
class DocumentCategory(MasterEntity): pass
class DocumentStatus(MasterEntity): pass
class DocumentVisibility(MasterEntity): pass
