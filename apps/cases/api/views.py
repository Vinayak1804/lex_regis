from rest_framework import viewsets
from rest_framework.decorators import action
from apps.common.api.responses import SuccessResponse, ValidationErrorResponse, NotFoundResponse
from .serializers import CaseSerializer, CaseTimelineSerializer
from apps.cases.services import CaseCreationService, CaseAssignmentService, CaseStatusService
from apps.cases.selectors import CaseSelector
from apps.cases.models import Case
from django.shortcuts import get_object_or_404

class CaseViewSet(viewsets.ViewSet):
    def list(self, request):
        cases = CaseSelector().queryset
        serializer = CaseSerializer(cases, many=True)
        return SuccessResponse(data=serializer.data)

    def create(self, request):
        try:
            case = CaseCreationService.create_case(request.data, request.user)
            serializer = CaseSerializer(case)
            return SuccessResponse(data=serializer.data, message="Case created successfully")
        except Exception as e:
            return ValidationErrorResponse(errors=str(e))

    def retrieve(self, request, pk=None):
        case = get_object_or_404(Case, pk=pk)
        serializer = CaseSerializer(case)
        return SuccessResponse(data=serializer.data)

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        return SuccessResponse(message="Status updated")
        
    @action(detail=True, methods=['post'])
    def assign_lawyer(self, request, pk=None):
        return SuccessResponse(message="Lawyer assigned")
