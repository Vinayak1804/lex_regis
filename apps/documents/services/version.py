from django.db import transaction
from apps.documents.models import DocumentVersion
from .hash import DocumentHashService

class DocumentVersionService:
    @staticmethod
    @transaction.atomic
    def add_version(document, file_obj, user, change_notes=""):
        checksum = DocumentHashService.generate_hash(file_obj)
        
        # Determine correct version number
        if not document.versions.exists():
            new_version_num = 1
        else:
            new_version_num = document.version_number + 1
            
        version = DocumentVersion.objects.create(
            document=document,
            version_number=new_version_num,
            file=file_obj,
            file_size=file_obj.size,
            checksum=checksum,
            uploaded_by=user,
            change_notes=change_notes
        )
        
        document.version_number = new_version_num
        document.original_file = file_obj
        document.checksum = checksum
        document.file_size = file_obj.size
        document.save(update_fields=['version_number', 'original_file', 'checksum', 'file_size', 'updated_at'])
        return version
