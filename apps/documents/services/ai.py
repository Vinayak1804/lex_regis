import time
import logging
import traceback
from django.conf import settings
from apps.documents.models import Document, DocumentMetadata
from apps.ai.models import AIRequestLog

logger = logging.getLogger(__name__)

class DocumentAIService:
    @staticmethod
    def analyze_document(document: Document, user):
        document.ai_analysis_status = 'PROCESSING'
        document.save(update_fields=['ai_analysis_status', 'updated_at'])
        
        try:
            metadata, _ = DocumentMetadata.objects.get_or_create(document=document)
            
            if not metadata.extracted_text:
                raise ValueError("No extracted text available for AI analysis. Please run OCR first.")
                
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = (
                "You are an expert Legal AI assistant. Analyze the provided legal document text "
                "and return a JSON object with the following structure:\n"
                "{\n"
                "  \"summary\": \"Brief summary of the document\",\n"
                "  \"document_type\": \"Type of document (e.g. Contract, Court Order, Affidavit)\",\n"
                "  \"parties\": [\"Party A\", \"Party B\"],\n"
                "  \"important_dates\": [\"2026-08-19\"],\n"
                "  \"obligations\": [\"Obligation 1\"],\n"
                "  \"risks\": [\"Risk 1\"]\n"
                "}\n"
                "Only output valid JSON. Do not include markdown formatting or additional explanation."
            )
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Document Text:\n\n{metadata.extracted_text[:20000]}"} # limit to avoid token overflow
            ]
            
            start_time = time.time()
            model_name = getattr(settings, 'GROQ_MODEL', 'llama3-8b-8192')
            
            log = AIRequestLog(
                user=user,
                endpoint='chat.completions.create',
                model_name=model_name,
                prompt=str(messages)
            )
            
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.1,
                max_tokens=2048,
                response_format={"type": "json_object"}
            )
            
            latency = time.time() - start_time
            response_content = completion.choices[0].message.content
            
            import json
            parsed_analysis = json.loads(response_content)
            
            metadata.custom_metadata_json['ai_analysis'] = parsed_analysis
            metadata.ai_provider = 'Groq'
            metadata.save(update_fields=['custom_metadata_json', 'ai_provider'])
            
            document.ai_analysis_status = 'COMPLETED'
            document.save(update_fields=['ai_analysis_status', 'updated_at'])
            
            log.response = response_content
            log.status_code = 200
            log.is_success = True
            log.latency_ms = latency * 1000
            if hasattr(completion, 'usage') and completion.usage:
                log.prompt_tokens = completion.usage.prompt_tokens
                log.completion_tokens = completion.usage.completion_tokens
                log.total_tokens = completion.usage.total_tokens
            log.save()
            
            return True
            
        except Exception as e:
            logger.exception(f"AI analysis failed for document {document.id}: {e}")
            document.ai_analysis_status = 'FAILED'
            document.save(update_fields=['ai_analysis_status', 'updated_at'])
            
            # Log failure
            log = AIRequestLog(
                user=user,
                endpoint='document_analysis',
                model_name='unknown',
                prompt=f"Document {document.id}",
                is_success=False,
                error_message=str(e),
                traceback=traceback.format_exc(),
                status_code=500
            )
            log.save()
            return False
