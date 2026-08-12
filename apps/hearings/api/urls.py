from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HearingViewSet, AdjournmentViewSet

router = DefaultRouter()
router.register(r'hearings', HearingViewSet, basename='hearing')
router.register(r'adjournments', AdjournmentViewSet, basename='adjournment')

urlpatterns = [
    path('', include(router.urls)),
]
