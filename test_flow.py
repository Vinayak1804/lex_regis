import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.accounts.models import User
from apps.common.choices.system import RoleChoices
from apps.lawyer_portal.models import LawyerProfile
from apps.intake.models import LegalIssue, ConsultationRequest
from apps.cases.models import Case
from django.urls import reverse

def verify_flow():
    # Setup
    User.objects.filter(email='client1@test.com').delete()
    User.objects.filter(email='lawyer1@test.com').delete()
    
    client_user = User.objects.create_user(email='client1@test.com', password='password123', role=RoleChoices.CLIENT)
    lawyer_user = User.objects.create_user(email='lawyer1@test.com', password='password123', role=RoleChoices.ADVOCATE, first_name='TestLawyer')
    prof, _ = LawyerProfile.objects.get_or_create(user=lawyer_user, bar_council_number='1234')
    
    # 1. Client Logs In
    client = Client()
    client.login(username='client1@test.com', password='password123')
    
    # 2. Client fills wizard
    response = client.post(reverse('intake:wizard'), {
        'description': 'I have a property dispute in Mumbai with my landlord who is not returning the deposit.',
        'city': 'Mumbai',
        'state': 'Maharashtra',
        'urgency': 'THIS_WEEK',
        'budget': 'Flexible',
        'preferred_consultation': 'Video'
    })
    
    print("Wizard Post Status:", response.status_code)
    
    # It should redirect to triage results
    issue = LegalIssue.objects.get(user=client_user)
    print("Issue created:", issue.description)
    print("AI Analysis:", getattr(issue, 'ai_analysis', None))
    
    # 3. Client Books Lawyer (simulate matching)
    response = client.post(reverse('intake:book_lawyer', args=[issue.id]), {
        'lawyer_id': prof.id
    })
    print("Book Lawyer Status:", response.status_code)
    cr = ConsultationRequest.objects.get(issue=issue)
    print("Consultation Request Created. Status:", cr.status)
    
    # 4. Lawyer Logs In
    lawyer_client = Client()
    lawyer_client.login(username='lawyer1@test.com', password='password123')
    
    # 5. Lawyer Accepts
    response = lawyer_client.post(reverse('lawyer_portal:accept_request', args=[cr.id]))
    print("Lawyer Accept Status:", response.status_code)
    
    cr.refresh_from_db()
    print("Consultation Request Status After Accept:", cr.status)
    
    # Check if conversation is created
    from apps.communication.models import Conversation
    conv = Conversation.objects.filter(participants=client_user).filter(participants=lawyer_user).first()
    print("Conversation Created:", conv is not None)
    
    # 6. Convert to Case
    response = client.post(reverse('intake:convert_consultation', args=[cr.id]))
    print("Convert to Case Status:", response.status_code)
    
    cr.refresh_from_db()
    print("Case linked to CR:", cr.case is not None)
    print("Case Title:", cr.case.title if cr.case else None)

if __name__ == '__main__':
    verify_flow()
