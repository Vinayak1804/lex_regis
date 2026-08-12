from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel
from .case import Case
from .master import CaseStatus

class CaseStatusHistory(BaseModel):
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='status_history')
    previous_status = models.ForeignKey(CaseStatus, on_delete=models.SET_NULL, null=True, related_name='+')
    new_status = models.ForeignKey(CaseStatus, on_delete=models.PROTECT, related_name='+')
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.case.case_number}: {self.previous_status} -> {self.new_status}"
