from apps.hearings.models import Hearing, HearingStatus, HearingMode
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

class HearingPresenter:
    def __init__(self, user):
        self.user = user

    def get_queryset(self):
        qs = Hearing.objects.filter(is_active=True).select_related('case', 'court_room', 'presiding_judge').order_by('start_time')
        
        # Enforce Role-based permissions
        if hasattr(self.user, 'profile') and self.user.profile.client_type:
            qs = qs.filter(case__client=self.user.profile)
        elif hasattr(self.user, 'professional_profile'):
            qs = qs.filter(case__assigned_lawyer=self.user.professional_profile)
        elif not self.user.is_staff:
            qs = qs.none()
            
        return qs

    def build_list_context(self, search_query=None):
        queryset = self.get_queryset()
        
        # Dashboard KPIs
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        next_7_days = today_end + timedelta(days=7)
        
        today_count = queryset.filter(start_time__gte=today_start, start_time__lt=today_end).count()
        upcoming_count = queryset.filter(start_time__gte=today_end, start_time__lt=next_7_days).count()
        adjourned_postponed_count = queryset.filter(status__in=[HearingStatus.ADJOURNED, HearingStatus.POSTPONED]).count()
        virtual_count = queryset.filter(mode=HearingMode.VIRTUAL).count()

        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(case__title__icontains=search_query) |
                Q(case__case_number__icontains=search_query)
            )
            
        hearings = []
        for h in queryset:
            hearings.append({
                'id': h.id,
                'number': h.hearing_number if h.hearing_number else 'TBD',
                'title': getattr(h, 'title', f"Hearing {h.hearing_number}"),
                'case_title': h.case.title if h.case else 'Unlinked',
                'case_number': h.case.case_number if h.case else 'N/A',
                'start_time': h.start_time,
                'end_time': h.end_time,
                'courtroom': h.court_room.room_number if h.court_room else 'Unassigned',
                'status': h.get_status_display(),
                'status_raw': h.status,
                'mode': h.get_mode_display(),
                'priority': h.get_priority_display(),
                'type': h.get_hearing_type_display(),
            })
            
        return {
            'hearings': hearings,
            'search_query': search_query or '',
            'today_count': today_count,
            'upcoming_count': upcoming_count,
            'adjourned_postponed_count': adjourned_postponed_count,
            'virtual_count': virtual_count,
        }
