from django.utils import timezone
from apps.documents.models import Document
import logging

logger = logging.getLogger(__name__)

class DocumentOCRService:
    """
    Synchronous OCR Service that can later be wired to Celery.
    Extracts text from PDF documents.
    """
    
    @staticmethod
    def process(document: Document):
        document.ocr_status = 'PROCESSING'
        document.save(update_fields=['ocr_status'])
        
        try:
            extracted_text = ""
            
            # Use pypdf for native extraction
            try:
                import pypdf
                
                if document.original_file and document.original_file.name.lower().endswith('.pdf'):
                    with document.original_file.open('rb') as f:
                        reader = pypdf.PdfReader(f)
                        for page in reader.pages:
                            text = page.extract_text()
                            if text:
                                extracted_text += text + "\n"
                elif document.original_file and (document.original_file.name.lower().endswith('.txt') or document.original_file.name.lower().endswith('.md')):
                    with document.original_file.open('r') as f:
                        extracted_text = f.read()
                else:
                    # Not a PDF or text file
                    pass
            except ImportError:
                # pypdf not available
                logger.error("pypdf is not installed, cannot extract text natively.")
                
            if extracted_text.strip():
                # Store the extracted text in DocumentMetadata or directly if there's a field
                # Assuming DocumentMetadata has an extracted_text field
                from apps.documents.models import DocumentMetadata
                metadata, _ = DocumentMetadata.objects.get_or_create(document=document)
                metadata.extracted_text = extracted_text
                metadata.save(update_fields=['extracted_text'])
                
                document.ocr_status = 'COMPLETED'
            else:
                document.ocr_status = 'FAILED'
                
            document.save(update_fields=['ocr_status', 'updated_at'])
            return True
            
        except Exception as e:
            logger.exception(f"OCR processing failed for document {document.id}: {e}")
            document.ocr_status = 'FAILED'
            document.save(update_fields=['ocr_status', 'updated_at'])
            return False
