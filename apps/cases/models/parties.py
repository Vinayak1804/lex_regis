from django.db import models
from apps.common.models.base import BaseModel
from .case import Case

class CaseParty(BaseModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='parties')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=50, default='Opponent')
    advocate = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.role}) - {self.case.case_number}"
