from django.urls import path
from .presentation.views import HearingListView, HearingCreateView

app_name = 'hearings_ui'

urlpatterns = [
    path('', HearingListView.as_view(), name='list'),
    path('schedule/', HearingCreateView.as_view(), name='schedule'),
]
