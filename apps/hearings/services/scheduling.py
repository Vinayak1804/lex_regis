from django.db import transaction
from django.utils import timezone
from apps.hearings.models import Hearing, HearingSequence
from apps.hearings.models.master import HearingStatus
from .policy import SchedulingPolicyService

class SchedulingService:
    @staticmethod
    @transaction.atomic
    def schedule_hearing(case, date, time, duration, hearing_type, court_room=None, judge=None):
        # Validate against policy rules
        SchedulingPolicyService.validate_schedule(
            hearing_date=date,
            scheduled_time=time,
            duration=duration,
            court=case.court,
            court_room=court_room,
            judge=judge
        )
        
        # Sequence Number
        year = timezone.now().year
        hearing_number = HearingSequence.get_next_number(year)
        
        # Determine Status (Scheduled)
        status, _ = HearingStatus.objects.get_or_create(code='SCHEDULED', defaults={'name': 'Scheduled'})
        
        hearing = Hearing.objects.create(
            hearing_number=hearing_number,
            case=case,
            hearing_type=hearing_type,
            status=status,
            court_room=court_room,
            presiding_judge=judge,
            scheduled_date=date,
            scheduled_time=time,
            estimated_duration_minutes=duration
        )
        
        # Here we will publish Domain Events and Timeline later
        return hearing
