from apps.cases.services.timeline import CaseTimelineService

class DocumentTimelineService:
    @staticmethod
    def log_upload(document, user):
        CaseTimelineService.add_event(
            case=document.case,
            event_type='DOCUMENT_ADDED',
            description=f"{user.first_name} {user.last_name} uploaded document '{document.original_file.name}'",
            user=user,
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
