from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from ..models import Notification
from ..services import NotificationService

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notification_id = kwargs.get('pk')
        success = NotificationService.mark_as_read(notification_id, request.user)
        return JsonResponse({'success': success})

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        count = NotificationService.mark_all_as_read(request.user)
        return JsonResponse({'success': True, 'count': count})
