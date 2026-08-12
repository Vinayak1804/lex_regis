from typing import List, Optional
from django.utils import timezone
from apps.accounts.models import User
from ..models import Notification, NotificationType

class NotificationService:
    @staticmethod
    def create_notification(
        user: User, 
        title: str, 
        message: str, 
        notification_type: str = NotificationType.SYSTEM,
        target_url: Optional[str] = None
    ) -> Notification:
        return Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            target_url=target_url
        )

    @staticmethod
    def mark_as_read(notification_id: int, user: User) -> bool:
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            if not notification.is_read:
                notification.is_read = True
                notification.read_at = timezone.now()
                notification.save(update_fields=['is_read', 'read_at', 'updated_at'])
            return True
        except Notification.DoesNotExist:
            return False

    @staticmethod
    def mark_all_as_read(user: User) -> int:
        return Notification.objects.filter(user=user, is_read=False).update(
            is_read=True, 
            read_at=timezone.now()
        )
