import logging
from django.db import transaction
from django.utils import timezone
from apps.intake.models import ConsultationRequest
from apps.communication.models import Conversation, ConversationStatus, Message

logger = logging.getLogger(__name__)

class ConsultationService:
    @staticmethod
    @transaction.atomic
    def accept_consultation(request_id: int):
        consultation = ConsultationRequest.objects.select_for_update().get(id=request_id)
        
        if consultation.status not in [ConsultationRequest.StatusChoices.PENDING, ConsultationRequest.StatusChoices.WAITING]:
            raise ValueError(f"Cannot accept consultation in status {consultation.status}")
            
        consultation.status = ConsultationRequest.StatusChoices.ACCEPTED
        consultation.save()
        
        # Sync case status
        if consultation.case:
            from apps.cases.models.case import CaseStatus
            consultation.case.status = CaseStatus.CONSULTATION
            consultation.case.save()
        
        # Create or find conversation
        # Check if one already exists for this exact combination
        conversation = Conversation.objects.filter(
            case=consultation.case, 
            participants=consultation.client
        ).filter(participants=consultation.lawyer.user).first()
        
        if not conversation:
            conversation = Conversation.objects.create(
                case=consultation.case,
                status=ConversationStatus.ACTIVE
            )
            conversation.participants.add(consultation.client, consultation.lawyer.user)
        else:
            conversation.status = ConversationStatus.ACTIVE
            conversation.save()
            
        # Create system message
        Message.objects.create(
            conversation=conversation,
            sender=consultation.lawyer.user,
            content=f"Consultation Request Accepted. I have reviewed your preliminary details regarding '{consultation.issue.description[:50]}...'. How can I help you today?"
        )
        
        # Future: Create notification and audit event here
        
        return consultation, conversation

    @staticmethod
    @transaction.atomic
    def decline_consultation(request_id: int):
        consultation = ConsultationRequest.objects.select_for_update().get(id=request_id)
        
        if consultation.status not in [ConsultationRequest.StatusChoices.PENDING, ConsultationRequest.StatusChoices.WAITING]:
            raise ValueError(f"Cannot decline consultation in status {consultation.status}")
            
        consultation.status = ConsultationRequest.StatusChoices.DECLINED
        consultation.save()
        
        # Sync case status
        if consultation.case:
            from apps.cases.models.case import CaseStatus
            consultation.case.status = CaseStatus.CLOSED
            consultation.case.save()
        
        # Future: Notification to client
        return consultation
        
    @staticmethod
    @transaction.atomic
    def wait_consultation(request_id: int):
        consultation = ConsultationRequest.objects.select_for_update().get(id=request_id)
        
        if consultation.status != ConsultationRequest.StatusChoices.PENDING:
            raise ValueError(f"Cannot put consultation in waiting from status {consultation.status}")
            
        consultation.status = ConsultationRequest.StatusChoices.WAITING
        consultation.save()
        
        # Future: Notification to client
        return consultation

    @staticmethod
    @transaction.atomic
    def complete_consultation(request_id: int):
        consultation = ConsultationRequest.objects.select_for_update().get(id=request_id)
        
        if consultation.status != ConsultationRequest.StatusChoices.ACTIVE:
            raise ValueError(f"Cannot complete consultation in status {consultation.status}")
            
        consultation.status = ConsultationRequest.StatusChoices.COMPLETED
        consultation.save()
        
        return consultation

    @staticmethod
    @transaction.atomic
    def cancel_consultation(request_id: int, user):
        consultation = ConsultationRequest.objects.select_for_update().get(id=request_id)
        
        if user != consultation.client:
            raise PermissionError("Only the client can cancel.")
            
        if consultation.status not in [ConsultationRequest.StatusChoices.PENDING, ConsultationRequest.StatusChoices.WAITING]:
            raise ValueError("Can only cancel pending or waiting requests.")
            
        consultation.status = ConsultationRequest.StatusChoices.CANCELLED
        consultation.save()
        return consultation
