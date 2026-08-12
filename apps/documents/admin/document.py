from django.contrib import admin
from apps.common.admin.base import BaseAdmin
from apps.documents.models import Document, DocumentVersion, DocumentMetadata

class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('version_number', 'upload_time', 'uploaded_by', 'checksum')

class DocumentMetadataInline(admin.StackedInline):
    model = DocumentMetadata
    extra = 0

@admin.register(Document)
class DocumentAdmin(BaseAdmin):
    list_display = ('document_number', 'case', 'uploaded_by', 'status', 'upload_timestamp')
    search_fields = ('document_number', 'case__case_number')
    list_filter = ('status', 'document_type', 'blockchain_verification_status')
    inlines = [DocumentVersionInline, DocumentMetadataInline]
