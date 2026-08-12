from django.views.generic import TemplateView

class PublicHomeView(TemplateView):
    template_name = 'public_site/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add demo data for platform statistics
        context['stats'] = {
            'lawyers': '12,450+',
            'cases': '85,000+',
            'documents': '1.2M+',
            'states': '28',
            'satisfaction': '4.8/5',
            'response_time': '< 2 Hrs'
        }
        return context
