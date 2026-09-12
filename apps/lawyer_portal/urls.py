from django.urls import path
from .views import (
    LawyerLandingView, LawyerRegistrationWizardView,
    LawyerDashboardView, AcceptRequestView, DeclineRequestView, WaitRequestView,
    AcceptAILegalIntakeCaseView, DeclineAILegalIntakeCaseView
)

app_name = 'lawyer_portal'

urlpatterns = [
    path('', LawyerLandingView.as_view(), name='landing'),
    path('register/', LawyerRegistrationWizardView.as_view(), name='register'),
    path('dashboard/', LawyerDashboardView.as_view(), name='dashboard'),
    path('requests/<int:request_id>/accept/', AcceptRequestView.as_view(), name='accept_request'),
    path('requests/<int:request_id>/decline/', DeclineRequestView.as_view(), name='decline_request'),
    path('requests/<int:request_id>/wait/', WaitRequestView.as_view(), name='wait_request'),
    path('cases/<int:case_id>/accept/', AcceptAILegalIntakeCaseView.as_view(), name='accept_case'),
    path('cases/<int:case_id>/decline/', DeclineAILegalIntakeCaseView.as_view(), name='decline_case'),
]
