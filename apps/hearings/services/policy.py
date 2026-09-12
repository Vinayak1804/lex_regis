from django.core.exceptions import ValidationError
from datetime import time, datetime
from django.db.models import Q
from apps.cases.models.master import CourtHoliday
from apps.hearings.models import Hearing, JudgeSchedule

class SchedulingPolicyService:
    @staticmethod
    def validate_working_hours(start_time: datetime, end_time: datetime):
        if not (time(9, 0) <= start_time.time() <= time(17, 0)) or not (time(9, 0) <= end_time.time() <= time(17, 0)):
            raise ValidationError("Hearing must be scheduled within court working hours (09:00 - 17:00).")
            
    @staticmethod
    def is_holiday(court, date) -> bool:
        return CourtHoliday.objects.filter(court=court, date=date).exists()
        
    @staticmethod
    def check_court_room_availability(court_room, start_time: datetime, end_time: datetime, exclude_hearing_id=None):
        hearings = Hearing.objects.filter(
            court_room=court_room,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(status__in=['CANCELLED', 'ADJOURNED', 'POSTPONED'])
        
        if exclude_hearing_id:
            hearings = hearings.exclude(id=exclude_hearing_id)
            
        if hearings.exists():
            raise ValidationError("Courtroom is already booked for an overlapping time.")
                
    @staticmethod
    def check_judge_availability(judge, start_time: datetime, end_time: datetime):
        date = start_time.date()
        schedule = JudgeSchedule.objects.filter(judge=judge, date=date).first()
        if schedule and not schedule.is_available:
            raise ValidationError(f"Judge is on leave: {schedule.leave_reason}")
            
        if schedule:
            if start_time.time() < schedule.start_time or end_time.time() > schedule.end_time:
                raise ValidationError("Time is outside the judge's scheduled working hours for this day.")

    @staticmethod
    def check_lawyer_conflict(assigned_lawyer, start_time: datetime, end_time: datetime, exclude_hearing_id=None):
        if not assigned_lawyer:
            return
            
        hearings = Hearing.objects.filter(
            case__assigned_lawyer=assigned_lawyer,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exclude(status__in=['CANCELLED', 'ADJOURNED', 'POSTPONED'])
        
        if exclude_hearing_id:
            hearings = hearings.exclude(id=exclude_hearing_id)
            
        if hearings.exists():
            raise ValidationError("Assigned lawyer already has a hearing scheduled at this time.")

    @staticmethod
    def validate_schedule(start_time, end_time, case, court_room=None, judge=None, exclude_hearing_id=None):
        if end_time <= start_time:
            raise ValidationError("End time must be after start time.")
            
        SchedulingPolicyService.validate_working_hours(start_time, end_time)
        
        if case.court and hasattr(case, 'court_obj'): # Assuming there is a court foreign key, but in Case it's a CharField. Let's just pass if it's CharField.
            pass
            
        if court_room:
            SchedulingPolicyService.check_court_room_availability(court_room, start_time, end_time, exclude_hearing_id)
            
        if judge:
            SchedulingPolicyService.check_judge_availability(judge, start_time, end_time)
            
        if case.assigned_lawyer:
            SchedulingPolicyService.check_lawyer_conflict(case.assigned_lawyer, start_time, end_time, exclude_hearing_id)
            
        return True
