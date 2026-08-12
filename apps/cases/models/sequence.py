from django.db import models, transaction
from apps.common.models.base import BaseModel
from django.utils import timezone

class CaseSequence(BaseModel):
    year = models.PositiveIntegerField(unique=True)
    last_value = models.PositiveIntegerField(default=0)
    
    @classmethod
    def get_next_number(cls):
        year = timezone.now().year
        with transaction.atomic():
            sequence, created = cls.objects.select_for_update().get_or_create(year=year)
            sequence.last_value += 1
            sequence.save()
            return f"LR-{year}-{str(sequence.last_value).zfill(6)}"
