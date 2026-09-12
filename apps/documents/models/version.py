from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.common.utilities.paths import get_document_upload_path
from .document import Document

class DocumentVersion(BaseModel):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    file = models.FileField(upload_to=get_document_upload_path)
    file_size = models.PositiveIntegerField(default=0)
    checksum = models.CharField(max_length=64, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    change_notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('document', 'version_number')
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.document.document_number} - v{self.version_number}"
