from django.urls import path
from .views import (
    RequestConsultationView, IncomingRequestsView, 
    AcceptRequestView, DeclineRequestView, MessagesView,
    ConversationDetailAPIView
)

app_name = 'communication'

urlpatterns = [
    path('request/<int:lawyer_id>/', RequestConsultationView.as_view(), name='request_consultation'),
    path('lawyer/incoming/', IncomingRequestsView.as_view(), name='incoming_requests'),
    path('lawyer/request/<int:pk>/accept/', AcceptRequestView.as_view(), name='accept_request'),
    path('lawyer/request/<int:pk>/decline/', DeclineRequestView.as_view(), name='decline_request'),
    path('messages/', MessagesView.as_view(), name='messages'),
    path('api/conversations/<int:pk>/', ConversationDetailAPIView.as_view(), name='conversation_api'),
]
