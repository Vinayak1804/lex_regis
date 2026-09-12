import time
from typing import Optional, List
from django.db import transaction
from ..models import Conversation, Message
from apps.accounts.models import User
from apps.cases.models import Case
from apps.documents.models import Document

class AIChatService:
    @staticmethod
    def get_or_create_conversation(user: User, case: Optional[Case] = None, document: Optional[Document] = None) -> Conversation:
        if case or document:
            # Try to find specific conversation
            qs = Conversation.objects.filter(user=user)
            if case:
                qs = qs.filter(case=case)
            if document:
                qs = qs.filter(document=document)
            
            conv = qs.first()
            if conv:
                return conv
                
        # Or create new
        title = "New Conversation"
        if case:
            title = f"Discussion on {case.title}"
        elif document:
            title = f"Analysis of {document.title if hasattr(document, 'title') else document.original_file.name}"
            
        return Conversation.objects.create(
            user=user,
            case=case,
            document=document,
            title=title
        )
        
    @staticmethod
    @transaction.atomic
    def process_user_message(conversation: Conversation, content: str) -> List[Message]:
        # Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            sender='USER',
            content=content,
            token_count=len(content.split())
        )
        
        # AI logic: generate response based on intent
        ai_response_content = AIChatService._generate_ai_response(content, conversation)
        
        # Simulate slight delay
        time.sleep(1)
        
        # Save AI message
        ai_message = Message.objects.create(
            conversation=conversation,
            sender='AI',
            content=ai_response_content,
            token_count=len(ai_response_content.split())
        )
        
        return [user_message, ai_message]
        
    @staticmethod
    def _generate_ai_response(query: str, conversation: Conversation) -> str:
        from django.conf import settings
        from groq import Groq
        import logging
        import time
        import traceback
        from apps.ai.models import AIRequestLog
        
        logger = logging.getLogger('apps')
        start_time = time.time()
        
        # Prepare the log record
        log = AIRequestLog(
            user=conversation.user,
            endpoint='chat.completions.create',
            model_name=getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-120b'),
        )
        
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = "You are Lex AI, a highly advanced, professional, and knowledgeable legal assistant for the Lex Regis Enterprise LegalTech Platform. You answer questions accurately, reference Indian Law context where applicable, and maintain a highly professional tone."
            
            if conversation.case:
                c = conversation.case
                system_prompt += f"\n\nYou are currently assisting the user with Case: '{c.title}' (Number: {c.case_number}).\nContext:\n- Client: {c.client.user.first_name if c.client else 'Unknown'}\n- Assigned Lawyer: {c.assigned_lawyer.user.first_name if c.assigned_lawyer else 'Unassigned'}\n- Practice Area: {c.practice_area}\n- Status: {c.get_status_display()}\n- Priority: {c.get_priority_display()}\n- Court: {c.court}\n- Description: {c.description}\nProvide highly tailored, specific advice for this matter."
                
            if conversation.document:
                d = conversation.document
                system_prompt += f"\n\nYou are currently assisting the user with a specific document.\nTitle: '{d.title if hasattr(d, 'title') else d.original_file.name}'\nType: {d.get_document_type_display() if hasattr(d, 'get_document_type_display') else 'Unknown'}\nPlease provide analysis focused on this document."
                
            messages = [
                {"role": "system", "content": system_prompt},
            ]
            
            past_messages = conversation.messages.all().order_by('-created_at')[:10]
            for msg in reversed(past_messages):
                role = "user" if msg.sender == 'USER' else "assistant"
                messages.append({"role": role, "content": msg.content})
                
            messages.append({"role": "user", "content": query})
            
            log.prompt = str(messages)
            logger.info(f"Sending Groq chat request for conversation {conversation.id} with {len(messages)} messages.")
            
            completion = client.chat.completions.create(
                model=log.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
            
            latency = time.time() - start_time
            logger.info(f"Groq chat request completed in {latency:.2f}s")
            
            response_content = completion.choices[0].message.content
            
            # Save successful metrics
            log.response = response_content
            log.status_code = 200
            log.is_success = True
            log.latency_ms = latency * 1000
            if hasattr(completion, 'usage') and completion.usage:
                log.prompt_tokens = completion.usage.prompt_tokens
                log.completion_tokens = completion.usage.completion_tokens
                log.total_tokens = completion.usage.total_tokens
            log.save()
            
            return response_content
            
        except Exception as e:
            logger.error(f"Groq API Error in Chat: {str(e)}\n{traceback.format_exc()}")
            log.status_code = getattr(e, 'status_code', 500)
            log.is_success = False
            log.latency_ms = (time.time() - start_time) * 1000
            log.error_message = str(e)
            log.traceback = traceback.format_exc()
            if not log.prompt:
                log.prompt = query
            log.save()
            raise
