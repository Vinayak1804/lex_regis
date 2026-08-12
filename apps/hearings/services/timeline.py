from apps.cases.services.timeline import CaseTimelineService

class HearingTimelineService:
    @staticmethod
    def log_hearing_scheduled(hearing, user):
        CaseTimelineService.log_event(
            case=hearing.case,
            actor=user,
            event_code='HEARING_SCHEDULED',
            category='HEARING',
            description=f"Hearing {hearing.hearing_number} scheduled for {hearing.scheduled_date}.",
            metadata={
                'hearing_id': str(hearing.id),
                'hearing_number': hearing.hearing_number,
                'scheduled_date': str(hearing.scheduled_date),
            }
        )

    @staticmethod
    def log_adjournment_requested(adjournment, user):
        CaseTimelineService.log_event(
            case=adjournment.hearing.case,
            actor=user,
            event_code='ADJOURNMENT_REQUESTED',
            category='HEARING',
            description=f"Adjournment requested for hearing {adjournment.hearing.hearing_number}.",
            metadata={
                'hearing_id': str(adjournment.hearing.id),
                'adjournment_id': str(adjournment.id)
            }
        )
