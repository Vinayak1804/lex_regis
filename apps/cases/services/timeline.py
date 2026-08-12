class CaseTimelineService:
    @staticmethod
    def add_event(case, event_type, description, user=None, metadata=None):
        from apps.cases.models import CaseTimeline
        return CaseTimeline.objects.create(
            case=case,
            actor=user,
            event_code=event_type,
            event_category='GENERAL',
            description=description,
            metadata=metadata or {}
        )
