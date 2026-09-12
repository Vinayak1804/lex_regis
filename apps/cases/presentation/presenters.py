from apps.cases.models.case import Case
from django.db.models import Q

class CasePresenter:
    def __init__(self, user):
        self.user = user

    def build_list_context(self, search_query=None, source_filter=None):
        queryset = Case.objects.select_related('client', 'assigned_lawyer').order_by('-created_at')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(case_number__icontains=search_query)
            )
            
        if source_filter:
            queryset = queryset.filter(matter_source=source_filter)
            
        return {
            'cases': queryset,
            'search_query': search_query or '',
            'current_filter': source_filter or 'ALL'
        }

    def build_detail_context(self, case_id):
        case = Case.objects.select_related('client', 'assigned_lawyer').get(id=case_id)
        
        # Ensure conversation exists
        from apps.communication.models import Conversation
        
        conversation = Conversation.objects.filter(case=case).first()
        if not conversation:
            conversation = Conversation.objects.create(case=case)
            if case.client and hasattr(case.client, 'user'):
                conversation.participants.add(case.client.user)
            if case.assigned_lawyer and hasattr(case.assigned_lawyer, 'user'):
                conversation.participants.add(case.assigned_lawyer.user)
            
        return {
            'case': case,
            'conversation': conversation,
            'messages': conversation.messages.select_related('sender').all() if conversation else []
        }
