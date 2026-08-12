from django.db import models
from django.utils import timezone
from apps.common.mixins.models import UUIDMixin, TimestampMixin, SoftDeleteMixin, OwnershipMixin, AuditMixin
from apps.common.managers.base import ActiveManager, SoftDeleteManager

class BaseModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, OwnershipMixin, AuditMixin):
    objects = models.Manager()
    active_objects = ActiveManager()
    available_objects = SoftDeleteManager()

    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.__class__.__name__} ({self.id})"

    def clean(self):
        super().clean()
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

    def restore(self, *args, **kwargs):
        self.is_deleted = False
        self.deleted_at = None
        self.save(*args, **kwargs)

    @property
    def is_soft_deleted(self):
        return self.is_deleted

    @property
    def is_recently_updated(self):
        return (timezone.now() - self.updated_at).days < 1
