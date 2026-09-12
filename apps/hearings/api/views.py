from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.api.responses import SuccessResponse, ValidationErrorResponse
from apps.hearings.models import Hearing, Adjournment
from apps.cases.models import Case
from apps.cases.models.master import CourtRoom
from apps.hearings.models.master import AdjournmentReason
from apps.hearings.services.scheduling import SchedulingService
from .serializers import HearingSerializer, CalendarEventSerializer

class HearingViewSet(viewsets.ModelViewSet):
    serializer_class = HearingSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Hearing.objects.select_related('case', 'court_room', 'presiding_judge').all()
        
        # Enforce Role-based permissions
        if hasattr(user, 'profile') and user.profile.client_type:
            # It's a client
            qs = qs.filter(case__client=user.profile)
        elif hasattr(user, 'professional_profile'):
            # It's a lawyer
            qs = qs.filter(case__assigned_lawyer=user.professional_profile)
        elif not user.is_staff:
            # Unauthorized fallback
            qs = qs.none()
            
        return qs

    @action(detail=False, methods=['GET'])
    def events(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        
        qs = self.get_queryset()
        if start and end:
            qs = qs.filter(start_time__gte=start, end_time__lte=end)
            
        serializer = CalendarEventSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def reschedule(self, request, pk=None):
        hearing = self.get_object()
        new_start = request.data.get('start_time')
        new_end = request.data.get('end_time')
        reason = request.data.get('reason', 'Rescheduled via calendar drag-and-drop')
        
        if not new_start or not new_end:
            return ValidationErrorResponse("start_time and end_time are required.")
            
        try:
            from django.utils.dateparse import parse_datetime
            start_dt = parse_datetime(new_start)
            end_dt = parse_datetime(new_end)
            
            updated_hearing = SchedulingService.reschedule_hearing(
                hearing=hearing,
                new_start_time=start_dt,
                new_end_time=end_dt,
                actor=request.user,
                reason=reason
            )
            return SuccessResponse(HearingSerializer(updated_hearing).data, message="Hearing rescheduled")
        except Exception as e:
            return ValidationErrorResponse(str(e))
