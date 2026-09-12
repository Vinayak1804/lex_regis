from django.urls import path
from . import views
from .views import (
    IntakeLandingView, 
    LearnMoreView,
    IntakeWizardView, 
    TalkToLawyerWizardView,
    TriageResultsView, 
    BookLawyerView,
    ClientConsultationStatusView,
    ConvertConsultationView,
    ConsultationChatbotAPIView,
    ConsultationRoomView
)

app_name = 'intake'

urlpatterns = [
    path('', IntakeLandingView.as_view(), name='landing'),
    path('learn-more/', LearnMoreView.as_view(), name='learn_more'),
    path('ai-intake/', IntakeWizardView.as_view(), name='wizard'),
    path('start/', TalkToLawyerWizardView.as_view(), name='talk_wizard'),
    path('<uuid:issue_id>/triage/', TriageResultsView.as_view(), name='triage_results'),
    path('<uuid:issue_id>/book/', BookLawyerView.as_view(), name='book_lawyer'),
    path('status/<uuid:request_id>/', ClientConsultationStatusView.as_view(), name='consultation_status'),
    path('room/<uuid:request_id>/', ConsultationRoomView.as_view(), name='room'),
    path('convert/<uuid:request_id>/', ConvertConsultationView.as_view(), name='convert_consultation'),
    path('api/chat/', ConsultationChatbotAPIView.as_view(), name='api_chat'),
    # AI Legal Intake API Routes
    path('api/ai-clarify/', views.AILegalIntakeClarifyAPIView.as_view(), name='api_ai_clarify'),
    path('api/ai-clarify/save/', views.AILegalIntakeSaveClarificationAPIView.as_view(), name='api_ai_clarify_save'),
    path('api/ai-upload/', views.AILegalIntakeUploadAPIView.as_view(), name='api_ai_upload'),
    path('api/ai-analyze/', views.AILegalIntakeAnalyzeAPIView.as_view(), name='api_ai_analyze'),
    path('api/ai-save-case/', views.AILegalIntakeSaveCaseAPIView.as_view(), name='api_ai_save_case'),
]
