from django.db import transaction
from django.core.exceptions import ValidationError
from apps.hearings.models import Adjournment, Hearing
from apps.hearings.models.master import HearingStatus
from .events import DomainEventService
from .scheduling import SchedulingService

class AdjournmentService:
    @staticmethod
    @transaction.atomic
    def request_adjournment(hearing, reason, requested_by, remarks=""):
        adjournment = Adjournment.objects.create(
            hearing=hearing,
            reason=reason,
            requested_by=requested_by,
            remarks=remarks
        )
        DomainEventService.publish_adjournment_requested(adjournment)
        return adjournment

    @staticmethod
    @transaction.atomic
    def grant_adjournment(adjournment, granted_by, new_date, new_time, new_duration):
        adjournment.granted = True
        adjournment.granted_by = granted_by
        adjournment.new_scheduled_date = new_date
        adjournment.save(update_fields=['granted', 'granted_by', 'new_scheduled_date', 'updated_at'])
        
        hearing = adjournment.hearing
        hearing.adjournment_count += 1
        
        old_date = hearing.scheduled_date
        
        # We could also use the SchedulingService to validate and reschedule
        SchedulingService.schedule_hearing(
            case=hearing.case,
            date=new_date,
            time=new_time,
            duration=new_duration,
            hearing_type=hearing.hearing_type,
            court_room=hearing.court_room,
            judge=hearing.presiding_judge
        )
        
        # Mark the old hearing as adjourned
        adjourned_status, _ = HearingStatus.objects.get_or_create(code='ADJOURNED', defaults={'name': 'Adjourned'})
        hearing.status = adjourned_status
        hearing.save(update_fields=['status', 'adjournment_count', 'updated_at'])
        
        DomainEventService.publish_adjournment_granted(adjournment)
        DomainEventService.publish_hearing_rescheduled(hearing, old_date, new_date)
        
        return adjournment
