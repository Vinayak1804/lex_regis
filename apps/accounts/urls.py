from django.urls import path
from .presentation.views import (
    RoleSelectionView, LexRegisLoginView, LexRegisLogoutView, 
    RegisterView, ProfileView, SecuritySettingsView, UserPreferencesView
)

app_name = 'accounts'

urlpatterns = [
    path('client/login/', LexRegisLoginView.as_view(), name='client_login', kwargs={'role': 'client'}),
    path('lawyer/login/', LexRegisLoginView.as_view(), name='lawyer_login', kwargs={'role': 'lawyer'}),
    path('law-firm/login/', LexRegisLoginView.as_view(), name='law_firm_login', kwargs={'role': 'law_firm'}),
    path('admin/login/', LexRegisLoginView.as_view(), name='admin_login', kwargs={'role': 'admin'}),
    path('login/', LexRegisLoginView.as_view(), name='login'),
    path('logout/', LexRegisLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('security/', SecuritySettingsView.as_view(), name='security'),
    path('preferences/', UserPreferencesView.as_view(), name='preferences'),
]
