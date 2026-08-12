from apps.documents.models import Document
from django.db.models import Q

class DocumentPresenter:
    def __init__(self, user):
        self.user = user

    def build_list_context(self, search_query=None):
        queryset = Document.objects.filter(is_active=True).select_related('case').order_by('-created_at')
        
        if search_query:
            queryset = queryset.filter(
                Q(document_number__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
        docs = []
        for d in queryset:
            docs.append({
                'id': d.id,
                'title': d.original_file.name if d.original_file else f"Doc {d.document_number}",
                'type': d.document_type.name if d.document_type else 'Unknown',
                'case_title': d.case.title if d.case else 'Unlinked',
                'verification_status': d.blockchain_verification_status,
                'created_at': d.created_at,
            })
            
        return {
            'documents': docs,
            'search_query': search_query or ''
        }
