from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from apps.common.choices.system import RoleChoices
from apps.accounts.models import Profile, ProfessionalProfile, Organization, SecuritySettings, UserPreferences
import logging

logger = logging.getLogger('apps')

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Everyone gets a basic profile, security, and preferences
        Profile.objects.create(user=instance)
        SecuritySettings.objects.create(user=instance)
        UserPreferences.objects.create(user=instance)
        
        if instance.role == RoleChoices.ADVOCATE:
            ProfessionalProfile.objects.create(user=instance)
            logger.info(f"Created ProfessionalProfile for advocate {instance.email}")
            
        elif instance.role == RoleChoices.LAW_FIRM:
            Organization.objects.create(user=instance, firm_name=f"{instance.first_name} {instance.last_name} Law Firm")
            logger.info(f"Created Organization profile for law firm {instance.email}")
            
        logger.info(f"Created basic profile, security, and preferences for user {instance.email}")
