from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .presenters import DashboardPresenter

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = DashboardPresenter(self.request.user)
        context['dashboard'] = presenter.build_view_model()
        
        from apps.cases.models.case import Case
        from apps.intake.models import ConsultationRequest
        
        if self.request.user.role == 'CLIENT':
            context['my_matters'] = Case.objects.filter(client=self.request.user.profile).order_by('-created_at')
            context['pending_requests'] = ConsultationRequest.objects.filter(client=self.request.user, status='PENDING')
        
        return context

class ComingSoonView(LoginRequiredMixin, TemplateView):
    template_name = 'common/coming_soon.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['feature_name'] = self.kwargs.get('feature_name', 'This Feature')
        return context

from django.views.generic import View
from django.shortcuts import render
from ..services.search import GlobalSearchService

class GlobalSearchView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        results = GlobalSearchService.search(query)
        
        context = {
            'query': query,
            'results': results,
            'has_results': any(len(v) > 0 for v in results.values())
        }
        
        return render(request, 'dashboard/search_results.html', context)
