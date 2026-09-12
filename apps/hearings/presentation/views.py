from django.views.generic import TemplateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.common.utilities.htmx import is_htmx
from .presenters import HearingPresenter
from django.urls import reverse_lazy
from apps.hearings.services.scheduling import SchedulingService
from .forms import HearingScheduleForm
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError

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

class HearingCreateView(LoginRequiredMixin, FormView):
    template_name = 'hearings/schedule.html'
    form_class = HearingScheduleForm
    success_url = reverse_lazy('hearings_ui:list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Enforce Case selection limited to user's assigned cases if lawyer
        user = self.request.user
        if hasattr(user, 'professional_profile'):
            form.fields['case'].queryset = form.fields['case'].queryset.filter(assigned_lawyer=user.professional_profile)
        return form

    def form_valid(self, form):
        try:
            SchedulingService.schedule_hearing(
                case=form.cleaned_data['case'],
                start_time=form.cleaned_data['start_time'],
                end_time=form.cleaned_data['end_time'],
                title=form.cleaned_data.get('title', ''),
                hearing_type=form.cleaned_data['hearing_type'],
                mode=form.cleaned_data['mode'],
                priority=form.cleaned_data['priority'],
                court_room=form.cleaned_data.get('court_room'),
                judge=form.cleaned_data.get('presiding_judge'),
                notes=form.cleaned_data.get('notes', ''),
                actor=self.request.user
            )
            return HttpResponseRedirect(self.get_success_url())
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
