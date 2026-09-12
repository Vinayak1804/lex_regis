from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from apps.documents.models import Document, DocumentVersion
from apps.documents.services.upload import DocumentUploadService
from apps.documents.services.exceptions import DuplicateDocumentError
from apps.accounts.models import User

class TestDMSIntegrity(TestCase):
    def setUp(self):
        from apps.documents.models.master import DocumentType, DocumentCategory, DocumentStatus, DocumentVisibility
        from apps.cases.models import Case
        from apps.accounts.models import Profile, User
        
        self.doc_type = DocumentType.objects.create(name="Contract", code="CONTRACT")
        self.category = DocumentCategory.objects.create(name="Legal", code="LEGAL")
        self.status = DocumentStatus.objects.create(name="Draft", code="DRAFT")
        self.visibility = DocumentVisibility.objects.create(name="Private", code="PRIVATE")
        
        self.user_case = User.objects.create(email="client@example.com", first_name="C", last_name="C", role="CLIENT", password="123")
        self.client_profile = Profile.objects.get(user=self.user_case)
        self.case = Case.objects.create(title="Test Case", client=self.client_profile)

    def test_duplicate_document_upload_rejected(self):
        user = User.objects.create(email="test@example.com", first_name="T", last_name="U", role="ADVOCATE", password="123")
        
        file_content = b"This is a test document."
        uploaded_file = SimpleUploadedFile("test_doc.pdf", file_content, content_type="application/pdf")
        
        form_data = {
            'title': 'Test Doc 1',
            'description': 'Description',
            'document_type': self.doc_type,
            'category': self.category,
            'status': self.status,
            'visibility': self.visibility,
            'case': self.case
        }
        
        # Upload first time should succeed
        doc1 = DocumentUploadService.upload_document(form_data, uploaded_file, user)
        assert doc1.pk is not None
        
        # Uploading exact same content should raise DuplicateDocumentError
        uploaded_file2 = SimpleUploadedFile("test_doc_duplicate.pdf", file_content, content_type="application/pdf")
        
        with self.assertRaises(DuplicateDocumentError):
            DocumentUploadService.upload_document(form_data, uploaded_file2, user)
            
    def test_duplicate_document_force_upload(self):
        user = User.objects.create(email="test3@example.com", first_name="T", last_name="U", role="ADVOCATE", password="123")
        
        file_content = b"This is a test document force."
        uploaded_file = SimpleUploadedFile("test_force.pdf", file_content, content_type="application/pdf")
        
        form_data = {
            'title': 'Test Doc Force',
            'description': 'Description',
            'document_type': self.doc_type,
            'category': self.category,
            'status': self.status,
            'visibility': self.visibility,
            'case': self.case
        }
        
        # Upload first time
        DocumentUploadService.upload_document(form_data, uploaded_file, user)
        
        # Uploading exact same content WITH FORCE should succeed
        uploaded_file2 = SimpleUploadedFile("test_force_duplicate.pdf", file_content, content_type="application/pdf")
        
        doc2 = DocumentUploadService.upload_document(form_data, uploaded_file2, user, force=True)
        assert doc2.pk is not None

    def test_storage_calculation(self):
        user = User.objects.create(email="test2@example.com", first_name="T", last_name="U", role="ADVOCATE", password="123")
        from apps.documents.services.storage import DocumentStorageService
        
        # Reset any existing for precise test (or use transactional rollback provided by django_db)
        
        file_content1 = b"A" * 1024 # 1KB
        uploaded_file1 = SimpleUploadedFile("size_test.pdf", file_content1, content_type="application/pdf")
        
        DocumentUploadService.upload_document({
            'title': 'T1',
            'document_type': self.doc_type,
            'category': self.category,
            'status': self.status,
            'visibility': self.visibility,
            'case': self.case
        }, uploaded_file1, user)
        
        usage = DocumentStorageService.get_usage()
        assert usage['total_bytes'] >= 1024
