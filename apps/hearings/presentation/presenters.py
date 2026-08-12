from apps.hearings.models import Hearing
from django.db.models import Q

class HearingPresenter:
    def __init__(self, user):
        self.user = user

    def build_list_context(self, search_query=None):
        queryset = Hearing.objects.filter(is_active=True).select_related('case', 'court_room').order_by('scheduled_date', 'scheduled_time')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(case__title__icontains=search_query)
            )
            
        hearings = []
        for h in queryset:
            hearings.append({
                'id': h.id,
                'number': h.hearing_number if h.hearing_number else 'TBD',
                'title': getattr(h, 'title', f"Hearing {h.hearing_number}"),
                'case_title': h.case.title if h.case else 'Unlinked',
                'date': h.scheduled_date,
                'time': h.scheduled_time,
                'courtroom': h.court_room.name if h.court_room else 'Unassigned',
                'status': h.status.name if h.status else 'Unknown',
            })
            
        return {
            'hearings': hearings,
            'search_query': search_query or ''
        }
