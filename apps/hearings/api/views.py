from rest_framework import viewsets, status
from rest_framework.decorators import action
from apps.common.api.responses import SuccessResponse, ValidationErrorResponse
from apps.hearings.models import Hearing, Adjournment
from apps.cases.models import Case
from apps.cases.models.master import CourtRoom, HearingType
from apps.hearings.models.master import AdjournmentReason
from apps.hearings.services.scheduling import SchedulingService
from apps.hearings.services.adjournment import AdjournmentService
from .serializers import HearingSerializer, ScheduleHearingSerializer, AdjournmentRequestSerializer, AdjournmentGrantSerializer

class HearingViewSet(viewsets.ModelViewSet):
    queryset = Hearing.objects.select_related('case', 'court_room', 'presiding_judge', 'status').all()
    serializer_class = HearingSerializer

    @action(detail=False, methods=['POST'])
    def schedule(self, request):
        serializer = ScheduleHearingSerializer(data=request.data)
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
            
        data = serializer.validated_data
        
        try:
            case = Case.objects.get(id=data['case_id'])
            hearing_type = HearingType.objects.get(id=data['hearing_type_id'])
            court_room = CourtRoom.objects.get(id=data['court_room_id']) if data.get('court_room_id') else None
            # Fetch judge from User model in real scenario
            judge = request.user if data.get('presiding_judge_id') else None
            
            hearing = SchedulingService.schedule_hearing(
                case=case,
                date=data['scheduled_date'],
                time=data['scheduled_time'],
                duration=data['estimated_duration_minutes'],
                hearing_type=hearing_type,
                court_room=court_room,
                judge=judge
            )
            return SuccessResponse(HearingSerializer(hearing).data, message="Hearing scheduled successfully")
        except Exception as e:
            return ValidationErrorResponse(str(e))

class AdjournmentViewSet(viewsets.ModelViewSet):
    queryset = Adjournment.objects.select_related('hearing', 'requested_by').all()
    
    @action(detail=False, methods=['POST'], url_path='request/(?P<hearing_id>[^/.]+)')
    def request_adjournment(self, request, hearing_id=None):
        serializer = AdjournmentRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
            
        try:
            hearing = Hearing.objects.get(id=hearing_id)
            reason = AdjournmentReason.objects.get(id=serializer.validated_data['reason_id'])
            
            adj = AdjournmentService.request_adjournment(
                hearing=hearing,
                reason=reason,
                requested_by=request.user,
                remarks=serializer.validated_data.get('remarks', '')
            )
            return SuccessResponse({'adjournment_id': adj.id}, message="Adjournment requested")
        except Exception as e:
            return ValidationErrorResponse(str(e))
            
    @action(detail=True, methods=['POST'])
    def grant(self, request, pk=None):
        adjournment = self.get_object()
        serializer = AdjournmentGrantSerializer(data=request.data)
        if not serializer.is_valid():
            return ValidationErrorResponse(serializer.errors)
            
        data = serializer.validated_data
        try:
            AdjournmentService.grant_adjournment(
                adjournment=adjournment,
                granted_by=request.user,
                new_date=data['new_scheduled_date'],
                new_time=data['new_scheduled_time'],
                new_duration=data['new_duration_minutes']
            )
            return SuccessResponse({}, message="Adjournment granted and hearing rescheduled")
        except Exception as e:
            return ValidationErrorResponse(str(e))
