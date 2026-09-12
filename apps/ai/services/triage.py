import logging
import json
import time
import traceback
from django.conf import settings
from groq import Groq
from apps.intake.models import LegalIssue, AIAnalysis
from apps.ai.models import AIRequestLog

logger = logging.getLogger(__name__)

class AITriageService:
    @staticmethod
    def analyze_issue(issue: LegalIssue) -> AIAnalysis:
        start_time = time.time()
        
        log = AIRequestLog(
            user=issue.user,
            endpoint='chat.completions.create',
            model_name=getattr(settings, 'GROQ_MODEL', 'llama3-70b-8192'),
        )
        
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = """You are an AI legal triage assistant. Extract the following information from the user's legal issue description.
Respond strictly in JSON format with these exact keys:
- practice_area: string (e.g., "Family Law", "Property Law")
- category: string
- subcategory: string
- urgency_assessment: string (e.g., "Routine", "Urgent", "Emergency")
- complexity: string ("Low", "Medium", "High", "Critical")
- important_facts: list of strings
- lawyer_type: string
- required_documents: list of strings
- timeline_estimate: string
- cost_estimate: string
- preliminary_assessment: string (Must be one of: "Favorable", "Mixed", "Unfavorable", "Insufficient Data")
- assessment_reasoning: string
- missing_information: list of strings
- suggested_next_steps: list of strings
"""
            query = f"User Issue Description: {issue.description}\nBudget: {issue.budget}\nCity: {issue.city}\nUrgency Selected: {issue.urgency}"
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ]
            
            log.prompt = str(messages)
            
            completion = client.chat.completions.create(
                model=log.model_name,
                messages=messages,
                temperature=0.1,
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
            
            # Create or update AIAnalysis
            analysis, _ = AIAnalysis.objects.update_or_create(
                issue=issue,
                defaults={
                    'practice_area': data.get('practice_area', ''),
                    'category': data.get('category', ''),
                    'subcategory': data.get('subcategory', ''),
                    'complexity': data.get('complexity', ''),
                    'recommended_lawyer_type': data.get('lawyer_type', ''),
                    'suggested_documents': data.get('required_documents', []),
                    'important_keywords': data.get('important_facts', []),
                    'timeline_estimate': data.get('timeline_estimate', ''),
                    'cost_estimate': data.get('cost_estimate', ''),
                    'preliminary_assessment': data.get('preliminary_assessment', ''),
                    'assessment_reasoning': data.get('assessment_reasoning', ''),
                    'suggested_next_steps': data.get('suggested_next_steps', []),
                    'missing_information': data.get('missing_information', []),
                }
            )
            return analysis
            
        except Exception as e:
            logger.error(f"Groq API Error in Triage: {str(e)}\n{traceback.format_exc()}")
            log.status_code = getattr(e, 'status_code', 500)
            log.is_success = False
            log.latency_ms = (time.time() - start_time) * 1000
            log.error_message = str(e)
            log.traceback = traceback.format_exc()
            if not log.prompt:
                log.prompt = "Failed before prompt creation"
            log.save()
            # If Groq fails, we don't fake analysis, we raise it or return None so the UI can show unavailable state.
            raise e
