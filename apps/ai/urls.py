from django.urls import path
from .presentation.views import AIChatView, AIChatMessageCreateView, AIDiagnosticsView

app_name = 'ai'

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='chat'),
    path('chat/send/', AIChatMessageCreateView.as_view(), name='chat_send'),
    path('diagnostics/', AIDiagnosticsView.as_view(), name='diagnostics'),
]
