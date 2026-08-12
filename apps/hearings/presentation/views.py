from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.common.utilities.htmx import is_htmx
from .presenters import HearingPresenter

class HearingListView(LoginRequiredMixin, TemplateView):
    template_name = 'hearings/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q')
        presenter = HearingPresenter(self.request.user)
        context.update(presenter.build_list_context(search_query))
        
        if is_htmx(self.request):
            self.template_name = 'hearings/partials/hearing_table.html'
            
        return context

from django.views.generic import FormView
from django.urls import reverse_lazy
from apps.hearings.services.scheduling import SchedulingService
from .forms import HearingScheduleForm
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.exceptions import ValidationError

class HearingCreateView(LoginRequiredMixin, FormView):
    template_name = 'hearings/schedule.html'
    form_class = HearingScheduleForm
    success_url = reverse_lazy('hearings_ui:list')

    def form_valid(self, form):
        try:
            SchedulingService.schedule_hearing(
                case=form.cleaned_data['case'],
                date=form.cleaned_data['scheduled_date'],
                time=form.cleaned_data['scheduled_time'],
                duration=form.cleaned_data['estimated_duration_minutes'],
                hearing_type=form.cleaned_data['hearing_type'],
                court_room=form.cleaned_data.get('court_room'),
                judge=form.cleaned_data.get('presiding_judge')
            )
            return HttpResponseRedirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
