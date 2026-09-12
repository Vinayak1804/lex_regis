from django.db import transaction
from django.utils import timezone
from apps.hearings.models import Hearing, HearingSequence, HearingStatus, HearingAuditLog, HearingActionChoices
from apps.notifications.models.notification import Notification, NotificationType
from .policy import SchedulingPolicyService

class SchedulingService:
    @staticmethod
    def _create_audit_log(hearing, actor, action, old_value=None, new_value=None, reason=""):
        HearingAuditLog.objects.create(
            hearing=hearing,
            case=hearing.case,
            actor=actor,
            action=action,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )

    @staticmethod
    def _create_notifications(hearing, title, message):
        case = hearing.case
        # Notify Client
        if case.client and hasattr(case.client, 'user') and case.client.user:
            Notification.objects.create(
                user=case.client.user,
                notification_type=NotificationType.HEARING,
                title=title,
                message=message,
                target_url=f"/hearings/{hearing.id}/"
            )
        # Notify Lawyer
        if case.assigned_lawyer and hasattr(case.assigned_lawyer, 'user') and case.assigned_lawyer.user:
            Notification.objects.create(
                user=case.assigned_lawyer.user,
                notification_type=NotificationType.HEARING,
                title=title,
                message=message,
                target_url=f"/hearings/{hearing.id}/"
            )

    @staticmethod
    @transaction.atomic
    def schedule_hearing(case, start_time, end_time, title, hearing_type, mode, priority, court_room=None, judge=None, notes="", actor=None):
        SchedulingPolicyService.validate_schedule(
            start_time=start_time,
            end_time=end_time,
            case=case,
            court_room=court_room,
            judge=judge
        )
        
        year = timezone.now().year
        hearing_number = HearingSequence.get_next_number(year)
        
        hearing = Hearing.objects.create(
            hearing_number=hearing_number,
            case=case,
            title=title,
            hearing_type=hearing_type,
            status=HearingStatus.SCHEDULED,
            mode=mode,
            priority=priority,
            court_room=court_room,
            presiding_judge=judge,
            start_time=start_time,
            end_time=end_time,
            notes=notes
        )
        
        SchedulingService._create_audit_log(
            hearing=hearing,
            actor=actor,
            action=HearingActionChoices.CREATED,
            new_value={'start_time': start_time.isoformat(), 'end_time': end_time.isoformat()}
        )
        
        SchedulingService._create_notifications(
            hearing,
            title=f"Hearing Scheduled: {case.case_number}",
            message=f"A new hearing has been scheduled on {start_time.strftime('%b %d, %Y %I:%M %p')}."
        )
        
        return hearing

    @staticmethod
    @transaction.atomic
    def reschedule_hearing(hearing, new_start_time, new_end_time, actor=None, reason=""):
        SchedulingPolicyService.validate_schedule(
            start_time=new_start_time,
            end_time=new_end_time,
            case=hearing.case,
            court_room=hearing.court_room,
            judge=hearing.presiding_judge,
            exclude_hearing_id=hearing.id
        )
        
        old_val = {'start_time': hearing.start_time.isoformat(), 'end_time': hearing.end_time.isoformat()}
        new_val = {'start_time': new_start_time.isoformat(), 'end_time': new_end_time.isoformat()}
        
        hearing.start_time = new_start_time
        hearing.end_time = new_end_time
        hearing.save()
        
        SchedulingService._create_audit_log(
            hearing=hearing,
            actor=actor,
            action=HearingActionChoices.RESCHEDULED,
            old_value=old_val,
            new_value=new_val,
            reason=reason
        )
        
        SchedulingService._create_notifications(
            hearing,
            title=f"Hearing Rescheduled: {hearing.case.case_number}",
            message=f"Hearing has been rescheduled to {new_start_time.strftime('%b %d, %Y %I:%M %p')}."
        )
        
        return hearing

    @staticmethod
    @transaction.atomic
    def update_status(hearing, new_status, actor=None, reason="", outcome=""):
        old_val = {'status': hearing.status}
        new_val = {'status': new_status}
        
        hearing.status = new_status
        if outcome:
            hearing.hearing_outcome = outcome
        hearing.save()
        
        # Determine appropriate audit action based on status
        action = HearingActionChoices.COMPLETED if new_status == HearingStatus.COMPLETED else \
                 HearingActionChoices.ADJOURNED if new_status == HearingStatus.ADJOURNED else \
                 HearingActionChoices.CANCELLED if new_status == HearingStatus.CANCELLED else \
                 HearingActionChoices.POSTPONED if new_status == HearingStatus.POSTPONED else \
                 HearingActionChoices.RESCHEDULED
                 
        SchedulingService._create_audit_log(
            hearing=hearing,
            actor=actor,
            action=action,
            old_value=old_val,
            new_value=new_val,
            reason=reason
        )
        
        SchedulingService._create_notifications(
            hearing,
            title=f"Hearing Status Updated: {hearing.case.case_number}",
            message=f"Hearing status is now {new_status}."
        )
        
        return hearing
