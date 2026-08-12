from django.db.models import Q
from apps.cases.models import Case
from apps.documents.models import Document
from apps.hearings.models import Hearing
from apps.accounts.models import Profile

class GlobalSearchService:
    @staticmethod
    def search(query: str, limit: int = 5):
        if not query or len(query) < 2:
            return {'cases': [], 'documents': [], 'hearings': [], 'clients': []}
            
        cases = Case.objects.filter(
            Q(title__icontains=query) | Q(case_number__icontains=query)
        ).select_related('assigned_lawyer')[:limit]
        
        documents = Document.objects.filter(
            Q(document_number__icontains=query) | Q(description__icontains=query)
        ).select_related('case')[:limit]
        
        hearings = Hearing.objects.filter(
            Q(title__icontains=query) | Q(hearing_number__icontains=query)
        ).select_related('case')[:limit]
        
        clients = Profile.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        ).select_related('user')[:limit]
        
        return {
            'cases': cases,
            'documents': documents,
            'hearings': hearings,
            'clients': clients
        }
