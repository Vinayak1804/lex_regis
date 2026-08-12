from apps.cases.models.case import Case
from django.db.models import Q

class CasePresenter:
    def __init__(self, user):
        self.user = user

    def build_list_context(self, search_query=None):
        queryset = Case.objects.select_related('client', 'assigned_lawyer').order_by('-created_at')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(case_number__icontains=search_query)
            )
            
        return {
            'cases': queryset,
            'search_query': search_query or ''
        }

    def build_detail_context(self, case_id):
        case = Case.objects.select_related('client', 'assigned_lawyer', 'conversation').get(id=case_id)
        
        # Ensure conversation exists
        from apps.communication.models import Conversation
        conversation, created = Conversation.objects.get_or_create(case=case)
        if created and case.client and hasattr(case.client, 'user'):
            conversation.participants.add(case.client.user)
        if created and case.assigned_lawyer and hasattr(case.assigned_lawyer, 'user'):
            conversation.participants.add(case.assigned_lawyer.user)
            
        return {
            'case': case,
            'conversation': conversation,
            'messages': conversation.messages.select_related('sender').all()
        }
