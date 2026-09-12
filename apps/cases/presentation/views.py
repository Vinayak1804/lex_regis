from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.common.utilities.htmx import is_htmx
from .presenters import CasePresenter

class CaseListView(LoginRequiredMixin, TemplateView):
    template_name = 'cases/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q')
        source_filter = self.request.GET.get('source')
        presenter = CasePresenter(self.request.user)
        context.update(presenter.build_list_context(search_query, source_filter))
        
        if is_htmx(self.request):
            self.template_name = 'cases/partials/case_table.html'
            
        return context

class CaseDetailView(LoginRequiredMixin, TemplateView):
    template_name = 'cases/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = CasePresenter(self.request.user)
        context.update(presenter.build_detail_context(self.kwargs['pk']))
        return context

from django.views.generic import View
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from apps.cases.services.creation import CaseCreationService
from apps.accounts.models import Profile, ProfessionalProfile
from apps.cases.models.master import CaseType, Court, CaseCategory, Act, PoliceStation, Currency, TaskTemplate, HearingType, CasePriority, CourtLevel
from apps.cases.models.template import MatterTemplate
from apps.common.choices.system import RoleChoices

class CaseCreateView(LoginRequiredMixin, View):
    def get(self, request):
        # Provide master data for dropdowns
        context = {
            'clients': Profile.objects.all(),
            'advocates': ProfessionalProfile.objects.filter(user__role=RoleChoices.ADVOCATE),
        }
        return render(request, 'cases/create.html', context)

    def post(self, request):
        try:
            case = CaseCreationService.create_case(request.POST, request.FILES, request.user)
            messages.success(request, f"Case {case.case_number} created successfully.")
            return redirect(reverse('cases_ui:detail', kwargs={'pk': case.id}))
        except Exception as e:
            messages.error(request, f"Error creating case: {str(e)}")
            return redirect(reverse('cases_ui:create'))
