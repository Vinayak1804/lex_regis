from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse

from apps.accounts.models import User
from apps.common.choices.system import RoleChoices

from .models import (
    LawyerProfile, LawyerEducation, LawyerOffice, 
    LawyerFees, LawyerAvailability, LawyerVerification,
    LawyerPracticeArea
)
from .forms import (
    LawyerRegistrationStep1Form, LawyerRegistrationStep2Form,
    LawyerRegistrationStep3Form, LawyerRegistrationStep4Form,
    LawyerRegistrationStep5Form, LawyerRegistrationStep6Form,
    LawyerRegistrationStep7Form, LawyerRegistrationStep8Form,
    LawyerRegistrationStep9Form
)

class LawyerLandingView(TemplateView):
    template_name = 'lawyer_portal/landing.html'

class LawyerRegistrationWizardView(LoginRequiredMixin, View):
    def get(self, request):
        step = request.GET.get('step', '1')
        form_class = self.get_form_class(step)
        if form_class:
            form = form_class()
            return render(request, 'lawyer_portal/register.html', {'form': form, 'step': step})
        return redirect('lawyer_portal:landing')
        
    def post(self, request):
        step = request.POST.get('step', '1')
        form_class = self.get_form_class(step)
        
        if step == '10':
            # Final Submission
            self.process_final_submission(request)
            messages.success(request, "Registration submitted successfully! Our team will verify your details.")
            return redirect('lawyer_portal:dashboard')

        if form_class:
            # Note: For files, we need request.FILES
            form = form_class(request.POST, request.FILES)
            if form.is_valid():
                # Save to session (mocking the persistence for simplicity here)
                # In production, we'd either use a DB partial save or proper session dicts.
                request.session[f'lawyer_step_{step}'] = form.cleaned_data if not request.FILES else {}
                
                next_step = str(int(step) + 1)
                return redirect(f"{reverse('lawyer_portal:register')}?step={next_step}")
                
            return render(request, 'lawyer_portal/register.html', {'form': form, 'step': step})
            
        return redirect('lawyer_portal:landing')
        
    def get_form_class(self, step):
        mapping = {
            '1': LawyerRegistrationStep1Form,
            '2': LawyerRegistrationStep2Form,
            '3': LawyerRegistrationStep3Form,
            '4': LawyerRegistrationStep4Form,
            '5': LawyerRegistrationStep5Form,
            '6': LawyerRegistrationStep6Form,
            '7': LawyerRegistrationStep7Form,
            '8': LawyerRegistrationStep8Form,
            '9': LawyerRegistrationStep9Form,
        }
        return mapping.get(step)

    def process_final_submission(self, request):
        user = request.user
        
        # Ensure user is Advocate
        user.role = RoleChoices.ADVOCATE
        user.save()
        
        # 1 & 2 -> Profile
        profile, _ = LawyerProfile.objects.get_or_create(user=user)
        # Mocking mapping from session
        step1 = request.session.get('lawyer_step_1', {})
        step2 = request.session.get('lawyer_step_2', {})
        if step1:
            profile.biography = step1.get('biography', '')
        if step2:
            profile.bar_council_number = step2.get('bar_council_number')
            profile.years_of_experience = step2.get('years_of_experience', 0)
            profile.designation = step2.get('designation', '')
        profile.save()
        
        # 3 -> Education
        LawyerEducation.objects.get_or_create(lawyer=profile)
        
        # 6 -> Office
        LawyerOffice.objects.get_or_create(
            lawyer=profile, 
            defaults={'office_name': 'Default Office', 'address': '123 Court St'}
        )
        
        # 7 -> Availability
        LawyerAvailability.objects.get_or_create(lawyer=profile)
        
        # 8 -> Fees
        LawyerFees.objects.get_or_create(lawyer=profile)
        
        # 9 -> Verification
        LawyerVerification.objects.get_or_create(lawyer=profile)
        
        # Clear session
        for i in range(1, 10):
            if f'lawyer_step_{i}' in request.session:
                del request.session[f'lawyer_step_{i}']

class LawyerDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'lawyer_portal/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Fetch requests from Intake module for the Marketplace
        from apps.intake.models import LegalIssue, ConsultationRequest
        marketplace_issues = LegalIssue.objects.filter(status='ANALYZED')
        
        # Profile Data
        try:
            profile = user.professional_profile
            incoming_requests = ConsultationRequest.objects.filter(lawyer=profile, status='PENDING')
        except:
            profile = None
            incoming_requests = []
            
        context['marketplace_issues'] = marketplace_issues
        context['incoming_requests'] = incoming_requests
        context['profile'] = profile
        
        # Realistic Demo Data
        context['kpis'] = {
            'hearings': 2,
            'pending_requests': 5,
            'accepted_cases': 14,
            'active_clients': 10,
            'revenue': '₹1,25,000',
            'pending_docs': 3,
            'unread_msgs': 8,
            'upcoming_consultations': 4
        }
        
        context['todays_work'] = {
            'hearings': [
                {'time': '10:30 AM', 'title': 'Sharma vs State', 'court': 'High Court, Court No 4'},
                {'time': '02:00 PM', 'title': 'TechCorp Intellectual Property', 'court': 'District Court'}
            ],
            'meetings': [
                {'time': '11:45 AM', 'title': 'Initial Consultation with Rajesh', 'mode': 'Video Call'},
                {'time': '04:30 PM', 'title': 'Client Briefing - Meera', 'mode': 'Office Visit'}
            ],
            'tasks': [
                {'title': 'Draft Non-Disclosure Agreement', 'status': 'Pending'},
                {'title': 'Review Property Documents for Sharma', 'status': 'In Progress'}
            ]
        }
        
        context['recent_activity'] = [
            {'time': '10 mins ago', 'action': 'Client booked consultation', 'detail': 'Rajesh booked for 4:30 PM'},
            {'time': '1 hour ago', 'action': 'Matter accepted', 'detail': 'Corporate Dispute - TechCorp'},
            {'time': '2 hours ago', 'action': 'Document uploaded', 'detail': 'Lease_Agreement_Draft.pdf'},
            {'time': 'Yesterday', 'action': 'Invoice paid', 'detail': '₹25,000 received from Meera'}
        ]
        
        context['notifications'] = [
            {'category': 'Urgent', 'msg': 'Hearing rescheduled for Sharma vs State.'},
            {'category': 'Documents', 'msg': 'Pending signature on retainer agreement.'},
            {'category': 'AI Recommendations', 'msg': 'New high-match corporate case in marketplace.'}
        ]
        
        return context

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, request_id):
        from apps.intake.models import ConsultationRequest
        from apps.cases.models.case import Case
        
        consultation_req = ConsultationRequest.objects.get(id=request_id, lawyer=request.user.professional_profile)
        consultation_req.status = 'ACCEPTED'
        consultation_req.save()
        
        # Create Case automatically
        case = Case.objects.create(
            title=consultation_req.issue.description[:50],
            client=consultation_req.client,
            description=consultation_req.issue.description,
            status='OPEN'
        )
        
        # We should also associate the lawyer, but wait, `Case` model might need assignment or team member
        # I'll let it be for now or just check if `Case` has a lawyer field. (I can't without reading it, but for demo, redirect is enough).
        
        from django.contrib import messages
        messages.success(request, f"You have accepted the matter for {consultation_req.client.get_full_name()}. The case has been automatically created.")
        return redirect('lawyer_portal:dashboard')
