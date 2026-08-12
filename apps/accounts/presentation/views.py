from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from apps.accounts.models import User
from .forms import (
    UserRegistrationStep1Form, 
    UserRegistrationStep2Form, 
    UserRegistrationStep3Form,
    ProfileEditForm,
    ProfileForm,
    ProfessionalProfileForm,
    OrganizationForm,
    SecuritySettingsForm,
    UserPreferencesForm
)
from apps.common.choices.system import RoleChoices

class RoleSelectionView(TemplateView):
    template_name = 'authentication/role_selection.html'

from django.http import JsonResponse
from django.contrib.auth import authenticate, login
import json

class LexRegisLoginView(View):
    def get(self, request, *args, **kwargs):
        return redirect('public_site:home')

    def post(self, request, *args, **kwargs):
        role_expected = kwargs.get('role')
        
        # AJAX form submission via fetch handles URLSearchParams or JSON
        email = request.POST.get('username')
        password = request.POST.get('password')
        
        if not email or not password:
            # Maybe it's JSON?
            try:
                data = json.loads(request.body)
                email = data.get('username')
                password = data.get('password')
            except:
                pass
                
        if not email or not password:
            return JsonResponse({'success': False, 'message': 'Missing email or password'})

        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            if not user.is_active:
                return JsonResponse({'success': False, 'message': 'Inactive account'})
            
            # Map role URL param to RoleChoices
            role_map = {
                'client': RoleChoices.CLIENT,
                'lawyer': RoleChoices.ADVOCATE,
                'law_firm': RoleChoices.LAW_FIRM,
                'admin': RoleChoices.ADMIN
            }
            
            expected_role = role_map.get(role_expected)
            
            if expected_role and user.role != expected_role:
                return JsonResponse({'success': False, 'message': 'Role mismatch. Please select the correct role.'})
                
            login(request, user)
            
            # Determine redirect
            if user.role == RoleChoices.ADVOCATE:
                redirect_url = '/portal/lawyer/dashboard/'
            elif user.role == RoleChoices.ADMIN:
                redirect_url = '/admin/'
            elif user.role == RoleChoices.LAW_FIRM:
                redirect_url = '/lawfirm/dashboard/'
            else:
                redirect_url = '/client/dashboard/'
                
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
            
        else:
            return JsonResponse({'success': False, 'message': 'Incorrect email or password'})

class LexRegisLogoutView(LogoutView):
    next_page = reverse_lazy('public_site:home')

class RegisterView(View):
    def get(self, request, *args, **kwargs):
        step = request.GET.get('step', '1')
        if step == '1':
            form = UserRegistrationStep1Form()
            return render(request, 'accounts/register_step_1.html', {'form': form})
        elif step == '2':
            form = UserRegistrationStep2Form()
            return render(request, 'accounts/register_step_2.html', {'form': form})
        elif step == '3':
            form = UserRegistrationStep3Form()
            return render(request, 'accounts/register_step_3.html', {'form': form})
        return redirect('accounts:register')

    def post(self, request, *args, **kwargs):
        step = request.POST.get('step', '1')
        
        if step == '1':
            form = UserRegistrationStep1Form(request.POST)
            if form.is_valid():
                # Save data to session
                request.session['reg_step1'] = form.cleaned_data
                return render(request, 'accounts/register_step_2.html', {'form': UserRegistrationStep2Form()})
            return render(request, 'accounts/register_step_1.html', {'form': form})
            
        elif step == '2':
            form = UserRegistrationStep2Form(request.POST)
            if form.is_valid():
                request.session['reg_step2'] = form.cleaned_data
                return render(request, 'accounts/register_step_3.html', {'form': UserRegistrationStep3Form()})
            return render(request, 'accounts/register_step_2.html', {'form': form})
            
        elif step == '3':
            form = UserRegistrationStep3Form(request.POST)
            if form.is_valid():
                step1_data = request.session.get('reg_step1', {})
                step2_data = request.session.get('reg_step2', {})
                
                # Check OTP logic (mock for now)
                if form.cleaned_data['otp'] != '123456': # Mock OTP check
                    form.add_error('otp', 'Invalid OTP. Try 123456')
                    return render(request, 'accounts/register_step_3.html', {'form': form})
                
                # Create user
                user = User.objects.create_user(
                    email=step1_data.get('email'),
                    password=step1_data.get('password'),
                    first_name=step1_data.get('first_name'),
                    last_name=step1_data.get('last_name'),
                    phone_number=step1_data.get('phone_number'),
                    role=step2_data.get('role', RoleChoices.CLIENT)
                )
                
                messages.success(request, "Registration successful! Please login.")
                return redirect('accounts:login')
            return render(request, 'accounts/register_step_3.html', {'form': form})

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_form'] = ProfileEditForm(instance=user)
        context['profile_form'] = ProfileForm(instance=user.profile)
        
        if user.role == RoleChoices.ADVOCATE and hasattr(user, 'professional_profile'):
            context['professional_form'] = ProfessionalProfileForm(instance=user.professional_profile)
        if user.role == RoleChoices.LAW_FIRM and hasattr(user, 'organization_profile'):
            context['organization_form'] = OrganizationForm(instance=user.organization_profile)
            
        return context
        
    def post(self, request, *args, **kwargs):
        user = request.user
        tab = request.POST.get('tab', 'personal')
        
        if tab == 'personal':
            user_form = ProfileEditForm(request.POST, request.FILES, instance=user)
            profile_form = ProfileForm(request.POST, instance=user.profile)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Personal information updated successfully.")
        
        elif tab == 'professional' and user.role == RoleChoices.ADVOCATE:
            prof_form = ProfessionalProfileForm(request.POST, instance=user.professional_profile)
            if prof_form.is_valid():
                prof_form.save()
                messages.success(request, "Professional information updated successfully.")
                
        elif tab == 'organization' and user.role == RoleChoices.LAW_FIRM:
            org_form = OrganizationForm(request.POST, request.FILES, instance=user.organization_profile)
            if org_form.is_valid():
                org_form.save()
                messages.success(request, "Organization details updated successfully.")

        return redirect('accounts:profile')

class SecuritySettingsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = SecuritySettingsForm(instance=request.user.security_settings)
        return render(request, 'accounts/security.html', {'form': form})
        
    def post(self, request, *args, **kwargs):
        form = SecuritySettingsForm(request.POST, instance=request.user.security_settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Security settings updated.")
        return render(request, 'accounts/security.html', {'form': form})

class UserPreferencesView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = UserPreferencesForm(instance=request.user.preferences)
        return render(request, 'accounts/preferences.html', {'form': form})
        
    def post(self, request, *args, **kwargs):
        form = UserPreferencesForm(request.POST, instance=request.user.preferences)
        if form.is_valid():
            form.save()
            messages.success(request, "Preferences saved successfully.")
        return render(request, 'accounts/preferences.html', {'form': form})
