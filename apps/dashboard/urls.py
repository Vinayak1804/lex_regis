from django.urls import path
from django.views.generic import TemplateView
from .presentation.views import DashboardView, GlobalSearchView
from .presentation.calendar_view import CalendarView

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('search/', GlobalSearchView.as_view(), name='search'),
    path('profile/', TemplateView.as_view(template_name='dashboard/profile.html'), name='profile'),
    path('settings/', TemplateView.as_view(template_name='dashboard/settings.html'), name='settings'),
    path('notifications/', TemplateView.as_view(template_name='dashboard/notifications.html'), name='notifications'),
    path('ai/', TemplateView.as_view(template_name='dashboard/ai.html'), name='ai_assistant'),
    path('analytics/', TemplateView.as_view(template_name='dashboard/analytics.html'), name='analytics'),
    path('calendar/', CalendarView.as_view(), name='calendar'),
    path('blockchain/', TemplateView.as_view(template_name='dashboard/blockchain.html'), name='blockchain'),
    path('messages/', TemplateView.as_view(template_name='dashboard/messages.html'), name='messages'),
    path('payments/', TemplateView.as_view(template_name='dashboard/payments.html'), name='payments'),
]
