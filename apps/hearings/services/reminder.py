from apps.hearings.models import Hearing

class ReminderService:
    @staticmethod
    def send_upcoming_hearing_reminders():
        """
        Cron job to send reminders for hearings scheduled in the next 24-48 hours.
        """
        pass
