from typing import List, Optional
from ..models import Conversation, Message
from apps.accounts.models import User

class AIChatSelector:
    @staticmethod
    def get_user_conversations(user: User) -> List[Conversation]:
        return Conversation.objects.filter(user=user).select_related('case', 'document')
        
    @staticmethod
    def get_conversation(conv_id: int, user: User) -> Optional[Conversation]:
        try:
            return Conversation.objects.get(id=conv_id, user=user)
        except Conversation.DoesNotExist:
            return None
            
    @staticmethod
    def get_conversation_messages(conversation: Conversation) -> List[Message]:
        return conversation.messages.all()
