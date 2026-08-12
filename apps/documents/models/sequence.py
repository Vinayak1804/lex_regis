from django.db import models, transaction

class DocumentSequence(models.Model):
    year = models.PositiveIntegerField(unique=True)
    last_value = models.PositiveIntegerField(default=0)

    @classmethod
    def get_next_number(cls, year):
        with transaction.atomic():
            sequence, created = cls.objects.select_for_update().get_or_create(year=year)
            sequence.last_value += 1
            sequence.save()
            return f"DOC-{year}-{sequence.last_value:06d}"
