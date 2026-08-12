from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from apps.common.choices.system import LanguageChoices

class UserPreferences(BaseModel):
    """
    User Preferences, including AI and Blockchain settings.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    
    # General Preferences
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, choices=LanguageChoices.choices, default=LanguageChoices.EN)
    time_zone = models.CharField(max_length=50, default='UTC')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')
    dashboard_layout = models.JSONField(default=dict, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    # AI Preferences
    ai_enabled = models.BooleanField(default=True)
    ai_save_history = models.BooleanField(default=True)
    ai_suggestions = models.BooleanField(default=True)
    ai_preferred_provider = models.CharField(max_length=50, default='openai')
    ai_preferred_model = models.CharField(max_length=50, default='gpt-4o')
    ai_privacy_settings = models.JSONField(default=dict, blank=True)
    
    # Blockchain Settings
    blockchain_verification_enabled = models.BooleanField(default=False)
    wallet_address = models.CharField(max_length=100, blank=True, null=True)
    preferred_network = models.CharField(max_length=50, default='ethereum')
    blockchain_verification_preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Preferences - {self.user.email}"
