from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .presenters import (
    NationalAnalyticsPresenter,
    StateAnalyticsPresenter,
    AIAnalyticsPresenter,
    BlockchainAnalyticsPresenter
)

class NationalAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/national.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = NationalAnalyticsPresenter()
        context['dashboard'] = presenter.build_view_model()
        return context

class StateAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/state.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug', 'all')
        if slug == 'all':
            self.template_name = 'analytics/states_list.html'
            presenter = NationalAnalyticsPresenter()
        else:
            presenter = StateAnalyticsPresenter(slug)
        context['dashboard'] = presenter.build_view_model()
        return context

class CourtAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/coming_soon.html'

class AdvocateAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/coming_soon.html'

class ClientAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/coming_soon.html'

class HearingAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/coming_soon.html'

class DocumentAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/coming_soon.html'

class AIAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/ai.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = AIAnalyticsPresenter()
        context['dashboard'] = presenter.build_view_model()
        return context

class BlockchainAnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/blockchain.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        presenter = BlockchainAnalyticsPresenter()
        context['dashboard'] = presenter.build_view_model()
        return context
