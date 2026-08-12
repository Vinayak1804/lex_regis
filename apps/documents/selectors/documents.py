from apps.documents.models import Document
from apps.common.selectors.base import FilteringSelector, SearchSelector

class DocumentSelector(FilteringSelector, SearchSelector):
    def __init__(self):
        super().__init__(Document.active_objects.select_related('case', 'uploaded_by').all())
        
    def get_case_documents(self, case):
        return self.queryset.filter(case=case)
        
    def get_recent_documents(self, limit=10):
        return self.queryset.order_by('-upload_timestamp')[:limit]
        
    def get_verified_documents(self):
        return self.queryset.filter(blockchain_verification_status='VERIFIED')
