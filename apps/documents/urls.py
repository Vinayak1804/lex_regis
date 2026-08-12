from django.urls import path
from .presentation.views import DocumentListView, DocumentUploadView

app_name = 'documents_ui'

urlpatterns = [
    path('', DocumentListView.as_view(), name='list'),
    path('upload/', DocumentUploadView.as_view(), name='upload'),
]
