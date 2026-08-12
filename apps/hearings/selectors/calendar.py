from datetime import date
from django.db.models import QuerySet
from apps.hearings.models import Hearing, JudgeSchedule

class HearingCalendarSelector:
    @staticmethod
    def get_judge_agenda(judge_id: str, for_date: date) -> QuerySet:
        return Hearing.objects.filter(
            presiding_judge_id=judge_id,
            scheduled_date=for_date
        ).order_by('scheduled_time').select_related('case', 'court_room', 'status')

    @staticmethod
    def get_court_agenda(court_room_id: str, for_date: date) -> QuerySet:
        return Hearing.objects.filter(
            court_room_id=court_room_id,
            scheduled_date=for_date
        ).order_by('scheduled_time').select_related('case', 'presiding_judge', 'status')
        
    @staticmethod
    def get_case_hearings(case_id: str) -> QuerySet:
        return Hearing.objects.filter(
            case_id=case_id
        ).order_by('-scheduled_date', '-scheduled_time').select_related('court_room', 'presiding_judge', 'status')
