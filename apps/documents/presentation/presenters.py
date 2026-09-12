from apps.documents.models import Document, DocumentCategory
from django.db.models import Q
from apps.documents.services.storage import DocumentStorageService
from django.utils import timezone
from datetime import timedelta

class DocumentPresenter:
    def __init__(self, user):
        self.user = user

    def build_list_context(self, search_query=None, category_id=None, view_type=None):
        queryset = Document.objects.filter(is_active=True).select_related('case', 'document_type', 'category').order_by('-created_at')
        
        if search_query:
            queryset = queryset.filter(
                Q(document_number__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(original_file__icontains=search_query)
            )
            
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        if view_type == 'recent':
            queryset = queryset.filter(created_at__gte=timezone.now() - timedelta(days=7))
        elif view_type == 'signed':
            # Will be implemented fully when signatures are done
            queryset = queryset.filter(signature_status='COMPLETED')
            
        docs = []
        for d in queryset:
            docs.append({
                'id': d.id,
                'title': d.original_file.name.split('/')[-1] if d.original_file else f"Doc {d.document_number}",
                'type': d.document_type.name if d.document_type else 'Unknown',
                'category': d.category.name if d.category else 'Uncategorized',
                'case_title': d.case.title if d.case else 'Unlinked',
                'verification_status': getattr(d, 'blockchain_verification_status', 'N/A'),
                'created_at': d.created_at,
                'version': d.version_number,
            })
            
        categories = DocumentCategory.objects.filter(is_active=True).order_by('name')
            
        return {
            'documents': docs,
            'search_query': search_query or '',
            'storage': DocumentStorageService.get_usage(),
            'categories': categories,
            'current_category': int(category_id) if category_id else None,
            'current_view': view_type
        }
