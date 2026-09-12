import logging
import json
import time
import traceback
from django.conf import settings
from groq import Groq
from apps.intake.models import LegalIssue
from apps.ai.models import AIRequestLog

logger = logging.getLogger(__name__)

class AIClarificationService:
    @staticmethod
    def generate_questions(issue: LegalIssue) -> dict:
        start_time = time.time()
        
        log = AIRequestLog(
            user=issue.user,
            endpoint='chat.completions.create',
            model_name=getattr(settings, 'GROQ_MODEL', 'llama3-70b-8192'),
        )
        
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = """You are an AI legal triage assistant. 
Your goal is to briefly summarize your understanding of the user's situation and ask 2 to 3 dynamic, highly relevant follow-up questions to help structure and clarify the user's legal issue.
Do not ask for basic contact info or information they have already provided.
Focus on missing dates, notices, contracts, relationships, or evidence types.
Keep questions clear and understandable to a layperson.

Respond strictly in JSON format matching this schema:
{
  "understanding_summary": "A concise, conversational 1-2 sentence summary starting with 'It sounds like you are dealing with...'",
  "questions": [
    {
      "id": "q1",
      "text": "The question text",
      "type": "text" // Use "text", "textarea", or "choice"
    }
  ]
}
If type is "choice", you must provide an "options" array of strings.
"""
            query = f"User Issue Description:\n{issue.description}\n\nPlease generate 2-3 clarification questions."
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            log.prompt = str(messages)
            
            completion = client.chat.completions.create(
                model=log.model_name,
                messages=messages,
                temperature=0.4,
                response_format={"type": "json_object"}
            )
            
            latency = time.time() - start_time
            response_content = completion.choices[0].message.content
            
            log.response = response_content
            log.status_code = 200
            log.is_success = True
            log.latency_ms = latency * 1000
            if hasattr(completion, 'usage') and completion.usage:
                log.prompt_tokens = completion.usage.prompt_tokens
                log.completion_tokens = completion.usage.completion_tokens
                log.total_tokens = completion.usage.total_tokens
            log.save()
            
            data = json.loads(response_content)
            questions = data.get("questions", [])
            understanding_summary = data.get("understanding_summary", "")
            
            # Ensure safe bounds
            if not isinstance(questions, list):
                questions = []
            
            # Bound to max 3 questions
            return {
                "understanding_summary": understanding_summary,
                "questions": questions[:3]
            }
            
        except Exception as e:
            logger.error(f"Groq API Error in Clarification: {str(e)}\n{traceback.format_exc()}")
            log.status_code = getattr(e, 'status_code', 500)
            log.is_success = False
            log.latency_ms = (time.time() - start_time) * 1000
            log.error_message = str(e)
            log.traceback = traceback.format_exc()
            if not log.prompt:
                log.prompt = "Failed before prompt creation"
            log.save()
            return {"understanding_summary": "", "questions": []}
