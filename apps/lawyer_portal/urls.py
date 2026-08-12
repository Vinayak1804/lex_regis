from django.urls import path
from .views import (
    LawyerLandingView, LawyerRegistrationWizardView,
    LawyerDashboardView, AcceptRequestView
)

app_name = 'lawyer_portal'

urlpatterns = [
    path('', LawyerLandingView.as_view(), name='landing'),
    path('register/', LawyerRegistrationWizardView.as_view(), name='register'),
    path('dashboard/', LawyerDashboardView.as_view(), name='dashboard'),
    path('accept/<int:request_id>/', AcceptRequestView.as_view(), name='accept_request'),
]
