from django.urls import path
from .presentation.views import (
    DocumentListView, DocumentUploadView, DocumentDetailView, 
    DocumentDownloadView, TriggerDocumentAIView, SignatureRequestCreateView
)

app_name = 'documents_ui'

urlpatterns = [
    path('', DocumentListView.as_view(), name='list'),
    path('upload/', DocumentUploadView.as_view(), name='upload'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='detail'),
    path('<int:pk>/download/', DocumentDownloadView.as_view(), name='download'),
    path('<int:pk>/trigger-ai/', TriggerDocumentAIView.as_view(), name='trigger_ai'),
    path('<int:pk>/request-signature/', SignatureRequestCreateView.as_view(), name='request_signature'),
]
