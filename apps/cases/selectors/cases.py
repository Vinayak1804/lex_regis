from apps.cases.models import Case
from apps.common.selectors.base import FilteringSelector, SearchSelector

class CaseSelector(FilteringSelector, SearchSelector):
    def __init__(self):
        super().__init__(Case.active_objects.select_related('client').all())
        
    def get_pending_cases(self):
        from apps.cases.models.case import CaseStatus
        return self.queryset.filter(status=CaseStatus.PENDING_ACCEPTANCE)
        
    def get_lawyer_cases(self, lawyer_profile):
        return self.queryset.filter(assigned_lawyer=lawyer_profile)
        
    def get_citizen_cases(self, citizen_profile):
        return self.queryset.filter(client=citizen_profile)
        
    def get_recent_cases(self, limit=10):
        return self.queryset.order_by('-created_at')[:limit]
