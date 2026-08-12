from django.core.exceptions import ValidationError
from apps.documents.models import DocumentType, DocumentCategory

class DocumentValidationService:
    @staticmethod
    def validate_upload(data, file_obj, user):
        if not file_obj:
            raise ValidationError("File is required")
        
        if file_obj.size == 0:
            raise ValidationError("File cannot be empty")
            
        return True
