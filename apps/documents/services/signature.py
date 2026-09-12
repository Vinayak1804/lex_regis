from django.db import transaction
from django.utils import timezone
from apps.documents.models import (
    SignatureRequest, Signer, SignatureField, SignatureAuditEvent,
    SignatureRequestStatus, SignerStatus, SignatureEventTypes,
    DocumentVersion
)

class SignatureServiceError(Exception):
    pass

class SignatureService:
    @staticmethod
    @transaction.atomic
    def create_request(document_version_id, requester, expires_at=None, message=""):
        version = DocumentVersion.objects.get(id=document_version_id)
        
        request = SignatureRequest.objects.create(
            document_version=version,
            requester=requester,
            expires_at=expires_at,
            message=message
        )
        
        SignatureService.log_audit_event(
            signature_request=request,
            actor=requester,
            event_type=SignatureEventTypes.REQUEST_CREATED,
            metadata={'message': message}
        )
        return request

    @staticmethod
    @transaction.atomic
    def add_signer(signature_request, email, role="", user=None, signing_order=1):
        if signature_request.status != SignatureRequestStatus.DRAFT:
            raise SignatureServiceError("Can only add signers to DRAFT requests.")
            
        signer = Signer.objects.create(
            signature_request=signature_request,
            user=user,
            email=email,
            role=role,
            signing_order=signing_order
        )
        return signer

    @staticmethod
    @transaction.atomic
    def add_field(signer, page, x, y, width, height, field_type):
        if signer.signature_request.status != SignatureRequestStatus.DRAFT:
            raise SignatureServiceError("Can only add fields to DRAFT requests.")
            
        field = SignatureField.objects.create(
            signature_request=signer.signature_request,
            signer=signer,
            page=page,
            x=x,
            y=y,
            width=width,
            height=height,
            field_type=field_type
        )
        return field

    @staticmethod
    @transaction.atomic
    def send_request(signature_request, actor=None):
        if signature_request.status != SignatureRequestStatus.DRAFT:
            raise SignatureServiceError("Request must be in DRAFT to send.")
            
        if not signature_request.signers.exists():
            raise SignatureServiceError("Cannot send a request with no signers.")
            
        signature_request.status = SignatureRequestStatus.PENDING
        signature_request.save(update_fields=['status'])
        
        # Here we would typically integrate with the Notification service
        SignatureService.log_audit_event(
            signature_request=signature_request,
            actor=actor,
            event_type=SignatureEventTypes.REMINDER_SENT,
            metadata={'action': 'initial_send'}
        )
        return signature_request

    @staticmethod
    @transaction.atomic
    def sign_document(signer, actor=None, ip_address=None, user_agent=None, auth_method="Password"):
        if signer.signature_request.status not in [SignatureRequestStatus.PENDING, SignatureRequestStatus.PARTIALLY_SIGNED]:
            raise SignatureServiceError("Request is not open for signing.")
            
        if signer.status != SignerStatus.PENDING:
            raise SignatureServiceError("Signer has already responded.")
            
        # Verify sequence if required
        if signer.signature_request.signing_order_enabled:
            previous_signers = Signer.objects.filter(
                signature_request=signer.signature_request,
                signing_order__lt=signer.signing_order,
                status=SignerStatus.PENDING
            )
            if previous_signers.exists():
                raise SignatureServiceError("It is not yet your turn to sign.")

        signer.status = SignerStatus.SIGNED
        signer.signed_at = timezone.now()
        signer.save(update_fields=['status', 'signed_at'])
        
        SignatureService.log_audit_event(
            signature_request=signer.signature_request,
            actor=actor,
            signer=signer,
            event_type=SignatureEventTypes.SIGNATURE_APPLIED,
            ip_address=ip_address,
            user_agent=user_agent,
            auth_method=auth_method
        )
        
        # Check if complete
        pending_signers = signer.signature_request.signers.filter(status=SignerStatus.PENDING).count()
        if pending_signers == 0:
            SignatureService.complete_request(signer.signature_request, actor)
        else:
            signer.signature_request.status = SignatureRequestStatus.PARTIALLY_SIGNED
            signer.signature_request.save(update_fields=['status'])

    @staticmethod
    @transaction.atomic
    def complete_request(signature_request, actor=None):
        signature_request.status = SignatureRequestStatus.COMPLETED
        signature_request.completed_at = timezone.now()
        signature_request.save(update_fields=['status', 'completed_at'])
        
        SignatureService.log_audit_event(
            signature_request=signature_request,
            actor=actor,
            event_type=SignatureEventTypes.SIGNING_COMPLETED
        )
        
        # Finalize the document version logic
        # Typically here we would 'flatten' the PDF with the signatures
        # generate a new DocumentVersion representing the Signed copy, 
        # hash it, and anchor to blockchain.
        
        from apps.documents.services.version import DocumentVersionService
        from apps.documents.services.hash import DocumentHashService
        from django.core.files.base import ContentFile
        
        original_doc = signature_request.document_version.document
        old_file = signature_request.document_version.file
        
        # In a real implementation, we would use a library to draw signatures onto the PDF.
        # For now, we will just read the original bytes and save as a new version.
        old_file.open('rb')
        new_file_content = old_file.read()
        old_file.close()
        
        new_file = ContentFile(new_file_content, name=f"signed_{old_file.name.split('/')[-1]}")
        
        new_version = DocumentVersionService.add_version(
            document=original_doc,
            file_obj=new_file,
            user=signature_request.requester,
            change_notes=f"Signed copy for Request ID {signature_request.id}"
        )
        
        original_doc.signature_status = 'COMPLETED'
        original_doc.save(update_fields=['signature_status'])
        
        SignatureService.log_audit_event(
            signature_request=signature_request,
            actor=actor,
            event_type=SignatureEventTypes.SIGNED_DOCUMENT_CREATED,
            metadata={'new_version_id': new_version.id, 'hash': new_version.checksum}
        )
        
        # Anchor the newly signed document version to the blockchain
        from apps.blockchain.services.verification import BlockchainVerificationService
        BlockchainVerificationService.verify_document(original_doc)

    @staticmethod
    def log_audit_event(signature_request, event_type, actor=None, signer=None, ip_address=None, user_agent=None, auth_method="", metadata=None):
        metadata = metadata or {}
        return SignatureAuditEvent.objects.create(
            signature_request=signature_request,
            event_type=event_type,
            actor=actor,
            signer=signer,
            ip_address=ip_address,
            user_agent=user_agent,
            auth_method=auth_method,
            metadata=metadata
        )
