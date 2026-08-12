from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.common.utilities.htmx import is_htmx
from .presenters import DocumentPresenter

class DocumentListView(LoginRequiredMixin, TemplateView):
    template_name = 'documents/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q')
        presenter = DocumentPresenter(self.request.user)
        context.update(presenter.build_list_context(search_query))
        
        if is_htmx(self.request):
            self.template_name = 'documents/partials/document_table.html'
            
        return context

from django.views.generic import FormView
from django.urls import reverse_lazy
from apps.documents.services.upload import DocumentUploadService
from .forms import DocumentUploadForm
from django.http import HttpResponseRedirect

class DocumentUploadView(LoginRequiredMixin, FormView):
    template_name = 'documents/upload.html'
    form_class = DocumentUploadForm
    success_url = reverse_lazy('documents_ui:list')

    def form_valid(self, form):
        file_obj = self.request.FILES.get('file')
        if not file_obj:
            form.add_error('file', 'No file was submitted.')
            return self.form_invalid(form)
            
        DocumentUploadService.upload_document(form.cleaned_data, file_obj, self.request.user)
        return HttpResponseRedirect(self.get_success_url())
