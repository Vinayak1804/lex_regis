from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.cases.models import Case
from apps.cases.services.timeline import CaseTimelineService

@receiver(post_save, sender=Case)
def case_post_save(sender, instance, created, **kwargs):
    if created:
        CaseTimelineService.add_event(
            case=instance,
            event_type='CASE_CREATED',
            description='Case was registered in the system.',
            user=instance.client.user if instance.client else None
        )
