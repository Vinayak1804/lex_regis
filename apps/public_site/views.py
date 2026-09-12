from django.views.generic import TemplateView, ListView, DetailView
from apps.accounts.models import ProfessionalProfile
from django.db.models import Q

class PublicHomeView(TemplateView):
    template_name = 'public_site/home.html'

class AboutView(TemplateView):
    template_name = 'public_site/about.html'
    
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

class LawyerListView(ListView):
    model = ProfessionalProfile
    template_name = 'public_site/lawyer_list.html'
    context_object_name = 'lawyers'
    
    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        practice_area = self.request.GET.get('practice_area')
        city = self.request.GET.get('city')
        
        if q:
            qs = qs.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(designation__icontains=q))
        if practice_area:
            qs = qs.filter(practice_areas__icontains=practice_area)
        if city:
            qs = qs.filter(user__profile__city__icontains=city)
        return qs

class LawyerDetailView(DetailView):
    model = ProfessionalProfile
    template_name = 'public_site/lawyer_detail.html'
    context_object_name = 'lawyer'
