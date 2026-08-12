from django.urls import path
from .presentation.views import (
    NationalAnalyticsView,
    StateAnalyticsView,
    CourtAnalyticsView,
    AdvocateAnalyticsView,
    ClientAnalyticsView,
    AIAnalyticsView,
    BlockchainAnalyticsView,
    HearingAnalyticsView,
    DocumentAnalyticsView,
)

app_name = 'analytics'

urlpatterns = [
    path('', NationalAnalyticsView.as_view(), name='national'),
    path('states/', StateAnalyticsView.as_view(), name='states_list'),
    path('state/<slug:slug>/', StateAnalyticsView.as_view(), name='state_detail'),
    path('courts/', CourtAnalyticsView.as_view(), name='courts'),
    path('advocates/', AdvocateAnalyticsView.as_view(), name='advocates'),
    path('clients/', ClientAnalyticsView.as_view(), name='clients'),
    path('hearings/', HearingAnalyticsView.as_view(), name='hearings'),
    path('documents/', DocumentAnalyticsView.as_view(), name='documents'),
    path('blockchain/', BlockchainAnalyticsView.as_view(), name='blockchain'),
    path('ai/', AIAnalyticsView.as_view(), name='ai'),
]
