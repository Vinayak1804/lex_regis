from django.core.exceptions import ValidationError
from datetime import time, datetime
from apps.cases.models.master import CourtHoliday
from apps.hearings.models import Hearing, JudgeSchedule

class SchedulingPolicyService:
    @staticmethod
    def validate_working_hours(scheduled_time: time):
        if not (time(9, 0) <= scheduled_time <= time(17, 0)):
            raise ValidationError("Hearing must be scheduled within court working hours (09:00 - 17:00).")
            
    @staticmethod
    def is_holiday(court, date) -> bool:
        return CourtHoliday.objects.filter(court=court, date=date).exists()
        
    @staticmethod
    def check_court_room_availability(court_room, date, start_time: time, duration_minutes: int, exclude_hearing_id=None):
        """
        Basic conflict check: ensure the courtroom doesn't have an overlapping hearing.
        In a real implementation, this would calculate exact overlap.
        """
        hearings = Hearing.objects.filter(court_room=court_room, scheduled_date=date)
        if exclude_hearing_id:
            hearings = hearings.exclude(id=exclude_hearing_id)
            
        for h in hearings:
            if h.scheduled_time == start_time:
                raise ValidationError("Courtroom is already booked at this specific time.")
                
    @staticmethod
    def check_judge_availability(judge, date, start_time: time, duration_minutes: int):
        schedule = JudgeSchedule.objects.filter(judge=judge, date=date).first()
        if schedule and not schedule.is_available:
            raise ValidationError(f"Judge is on leave: {schedule.leave_reason}")
            
        if schedule:
            if start_time < schedule.start_time or start_time > schedule.end_time:
                raise ValidationError("Time is outside the judge's scheduled working hours for this day.")

    @staticmethod
    def validate_schedule(hearing_date, scheduled_time, duration, court, court_room, judge, exclude_hearing_id=None):
        SchedulingPolicyService.validate_working_hours(scheduled_time)
        
        if SchedulingPolicyService.is_holiday(court, hearing_date):
            raise ValidationError("The selected date is a court holiday.")
            
        if court_room:
            SchedulingPolicyService.check_court_room_availability(court_room, hearing_date, scheduled_time, duration, exclude_hearing_id)
            
        if judge:
            SchedulingPolicyService.check_judge_availability(judge, hearing_date, scheduled_time, duration)
            
        return True
