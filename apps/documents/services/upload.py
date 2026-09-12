from django.db import transaction
from django.utils import timezone
from apps.documents.models import Document, DocumentVersion, DocumentMetadata, DocumentSequence
from .validation import DocumentValidationService
from .storage import DocumentStorageService
from .hash import DocumentHashService
from .version import DocumentVersionService
from .timeline import DocumentTimelineService

class DocumentUploadService:
    @staticmethod
    @transaction.atomic
    def upload_document(data, file_obj, user, force=False):
        DocumentValidationService.validate_upload(data, file_obj, user)
        
        checksum = DocumentHashService.generate_hash(file_obj)
        
        if not force:
            existing = Document.objects.filter(checksum=checksum).first()
            if existing:
                from .exceptions import DuplicateDocumentError
                raise DuplicateDocumentError(f"Duplicate document detected.", document_id=existing.id)
        
        # Determine sequence year
        year = timezone.now().year
        doc_number = DocumentSequence.get_next_number(year)
        
        file_extension = file_obj.name.split('.')[-1].upper() if '.' in file_obj.name else ''
        
        document = Document.objects.create(
            document_number=doc_number,
            case=data.get('case'),
            uploaded_by=user,
            owner=data.get('owner', user),
            document_type=data.get('document_type'),
            category=data.get('category'),
            status=data.get('status', 'DRAFT'),
            visibility=data.get('visibility', 'PRIVATE'),
            original_file=file_obj,
            file_size=file_obj.size,
            file_extension=file_extension,
            mime_type=file_obj.content_type if hasattr(file_obj, 'content_type') else '',
            checksum=checksum,
            version_number=1,
            description=data.get('description', '')
        )
        # Document is already saved with original_file during create()
        version = DocumentVersionService.add_version(
            document=document,
            file_obj=file_obj,
            user=user,
            change_notes="Initial upload"
        )
        
        DocumentMetadata.objects.create(
            document=document
        )
        
        DocumentTimelineService.log_upload(document, user)
        
        return document
