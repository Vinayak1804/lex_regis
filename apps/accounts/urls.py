from django.urls import path
from .presentation.views import (
    RoleSelectionView, LexRegisLoginView, LexRegisLogoutView, 
    RegisterView, ProfileView, SecuritySettingsView, UserPreferencesView
)
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('client/login/', LexRegisLoginView.as_view(), name='client_login', kwargs={'role': 'client'}),
    path('lawyer/login/', LexRegisLoginView.as_view(), name='lawyer_login', kwargs={'role': 'lawyer'}),
    path('law-firm/login/', LexRegisLoginView.as_view(), name='law_firm_login', kwargs={'role': 'law_firm'}),
    path('admin/login/', LexRegisLoginView.as_view(), name='admin_login', kwargs={'role': 'admin'}),
    path('login/', RoleSelectionView.as_view(), name='login'),
    path('logout/', LexRegisLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('security/', SecuritySettingsView.as_view(), name='security'),
    path('preferences/', UserPreferencesView.as_view(), name='preferences'),
    
    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='authentication/password_reset_form.html',
        email_template_name='authentication/password_reset_email.html',
        success_url='/accounts/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='authentication/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='authentication/password_reset_confirm.html',
        success_url='/accounts/password-reset-complete/'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='authentication/password_reset_complete.html'
    ), name='password_reset_complete'),
]
