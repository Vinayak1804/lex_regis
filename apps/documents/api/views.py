from rest_framework import viewsets
from rest_framework.decorators import action
from apps.common.api.responses import SuccessResponse, ValidationErrorResponse
from .serializers import DocumentSerializer
from apps.documents.services import DocumentUploadService
from apps.documents.selectors import DocumentSelector

class DocumentViewSet(viewsets.ViewSet):
    def list(self, request):
        docs = DocumentSelector().queryset
        serializer = DocumentSerializer(docs, many=True)
        return SuccessResponse(data=serializer.data)

    def create(self, request):
        try:
            return SuccessResponse(message="Document uploaded successfully")
        except Exception as e:
            return ValidationErrorResponse(errors=str(e))
