from django.urls import path
from .views import IntakeLandingView, IntakeWizardView, LawyerRecommendationView, BookLawyerView

app_name = 'intake'

urlpatterns = [
    path('', IntakeLandingView.as_view(), name='landing'),
    path('start/', IntakeWizardView.as_view(), name='wizard'),
    path('<uuid:issue_id>/lawyers/', LawyerRecommendationView.as_view(), name='lawyers'),
    path('<uuid:issue_id>/book/', BookLawyerView.as_view(), name='book_lawyer'),
]
