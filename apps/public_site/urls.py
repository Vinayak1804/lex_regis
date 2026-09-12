from django.urls import path
from .views import PublicHomeView, AboutView, LawyerListView, LawyerDetailView

app_name = 'public_site'

urlpatterns = [
    path('', PublicHomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('lawyers/', LawyerListView.as_view(), name='lawyer_list'),
    path('lawyers/<int:pk>/', LawyerDetailView.as_view(), name='lawyer_detail'),
]
