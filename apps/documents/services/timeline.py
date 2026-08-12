from apps.cases.services.timeline import CaseTimelineService

class DocumentTimelineService:
    @staticmethod
    def log_upload(document, user):
        CaseTimelineService.log_event(
            case=document.case,
            actor=user,
            event_code='DOCUMENT_UPLOADED',
            category='DOCUMENT',
            description=f"Document {document.document_number} uploaded.",
            metadata={
                'document_id': str(document.id),
                'document_number': document.document_number,
                'file_name': document.original_file.name
            }
        )

    @staticmethod
    def log_new_version(version, user):
        CaseTimelineService.log_event(
            case=version.document.case,
            actor=user,
            event_code='DOCUMENT_VERSION_ADDED',
            category='DOCUMENT',
            description=f"Version {version.version_number} added to Document {version.document.document_number}.",
            metadata={
                'document_id': str(version.document.id),
                'version_id': str(version.id),
                'version_number': version.version_number
            }
        )
