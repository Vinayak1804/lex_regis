from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.documents.models import Document

@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    pass
