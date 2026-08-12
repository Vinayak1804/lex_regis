from apps.documents.models import Document
from apps.documents.services.hash import DocumentHashService

class DocumentDeduplicationService:
    @staticmethod
    def check_duplicate(file_obj, case=None) -> Document:
        \"\"\"
        Check if an identical document exists based on SHA256 checksum.
        If case is provided, restricts deduplication scope to the specific case.
        Returns the existing Document if found, else None.
        \"\"\"
        checksum = DocumentHashService.generate_hash(file_obj)
        qs = Document.objects.filter(checksum=checksum)
        
        if case:
            qs = qs.filter(case=case)
            
        return qs.first()
