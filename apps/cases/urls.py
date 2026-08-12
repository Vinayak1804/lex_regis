from django.urls import path
from .presentation.views import CaseListView, CaseDetailView, CaseCreateView

app_name = 'cases_ui'

urlpatterns = [
    path('', CaseListView.as_view(), name='list'),
    path('create/', CaseCreateView.as_view(), name='create'),
    path('<uuid:pk>/', CaseDetailView.as_view(), name='detail'),
]
