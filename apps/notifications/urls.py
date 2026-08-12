from django.urls import path
from .presentation.views import NotificationListView, MarkNotificationReadView, MarkAllNotificationsReadView

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('<int:pk>/read/', MarkNotificationReadView.as_view(), name='mark_read'),
    path('read-all/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
]
