from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.hearings.models import Hearing

class CalendarView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/calendar.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We can pass upcoming hearings to be rendered on the calendar
        # A real calendar would use an API endpoint to fetch events asynchronously
        context['hearings'] = Hearing.objects.filter(is_active=True).select_related('case')
        return context
