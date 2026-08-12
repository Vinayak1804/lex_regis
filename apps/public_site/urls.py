from django.urls import path
from .views import PublicHomeView

app_name = 'public_site'

urlpatterns = [
    path('', PublicHomeView.as_view(), name='home'),
]
