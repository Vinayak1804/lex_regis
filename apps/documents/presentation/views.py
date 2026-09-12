from django.views.generic import TemplateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.common.utilities.htmx import is_htmx
from apps.documents.models import Document
from .presenters import DocumentPresenter
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
import os

class DocumentListView(LoginRequiredMixin, TemplateView):
    template_name = 'documents/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q')
        category_id = self.request.GET.get('category')
        view_type = self.request.GET.get('view')
        
        presenter = DocumentPresenter(self.request.user)
        context.update(presenter.build_list_context(search_query, category_id, view_type))
        
        if is_htmx(self.request):
            self.template_name = 'documents/partials/document_table.html'
            
        return context

from django.views.generic import FormView
from django.urls import reverse_lazy
from apps.documents.services.upload import DocumentUploadService
from .forms import DocumentUploadForm
from django.http import HttpResponseRedirect
from apps.documents.services.exceptions import DuplicateDocumentError

class DocumentUploadView(LoginRequiredMixin, FormView):
    template_name = 'documents/upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('documents_ui:list')

    def form_valid(self, form):
        file_obj = self.request.FILES.get('file')
        if not file_obj:
            form.add_error('file', 'No file was submitted.')
            return self.form_invalid(form)
            
        force = self.request.POST.get('force_upload') == 'true'
        try:
            doc = DocumentUploadService.upload_document(form.cleaned_data, file_obj, self.request.user, force=force)
            # Automatically trigger OCR natively
            from apps.documents.services.ocr import DocumentOCRService
            from apps.documents.services.ai import DocumentAIService
            from apps.blockchain.services.verification import BlockchainVerificationService
            
            DocumentOCRService.process(doc)
            DocumentAIService.analyze_document(doc, self.request.user)
            BlockchainVerificationService.verify_document(doc)
            
            return HttpResponseRedirect(self.get_success_url())
        except DuplicateDocumentError as e:
            return self.render_to_response(self.get_context_data(
                form=form, 
                duplicate_error=str(e),
                duplicate_document_id=e.document_id
            ))

class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'documents/detail.html'
    context_object_name = 'document'
    
    def get_queryset(self):
        # Enforce basic object-level visibility for now (Client vs Lawyer logic would go here)
        return Document.objects.filter(is_active=True)

class DocumentDownloadView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        document = get_object_or_404(Document, pk=pk, is_active=True)
        # Verify permissions: e.g. if case is present, does user have access to case?
        # (Simplified permission check, should be expanded based on case permissions)
        if document.visibility == 'CONFIDENTIAL' and request.user.role == 'CLIENT':
            # Example check - replace with real logic if needed
            pass 
            
        file_obj = document.original_file
        if not file_obj:
            raise Http404("File not found")
            
        response = HttpResponse(file_obj.read(), content_type=document.mime_type or 'application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_obj.name)}"'
        return response

class TriggerDocumentAIView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        document = get_object_or_404(Document, pk=pk, is_active=True)
        from apps.documents.services.ai import DocumentAIService
        DocumentAIService.analyze_document(document, request.user)
        return redirect('documents_ui:detail', pk=pk)

class SignatureRequestCreateView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        document = get_object_or_404(Document, pk=pk, is_active=True)
        signer_email = request.POST.get('signer_email')
        message = request.POST.get('message', '')
        
        if signer_email:
            from apps.documents.services.signature import SignatureService
            latest_version = document.versions.order_by('-version_number').first()
            if latest_version:
                sig_request = SignatureService.create_request(
                    document_version_id=latest_version.id,
                    requester=request.user,
                    message=message
                )
                SignatureService.add_signer(
                    signature_request=sig_request,
                    email=signer_email,
                    role="Signatory"
                )
                SignatureService.send_request(sig_request, actor=request.user)
                
                # Update document signature status
                document.signature_status = 'PENDING'
                document.save(update_fields=['signature_status'])
                
        return redirect('documents_ui:detail', pk=pk)
