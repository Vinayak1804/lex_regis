import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User, Profile, ProfessionalProfile
from apps.cases.models.case import Case, CaseStatus
from apps.communication.models import Conversation, Message, ConversationStatus
from apps.common.choices.system import RoleChoices
from django.utils import timezone
from datetime import timedelta

def seed_demo_data():
    print("Starting demo seeding...")

    # 1. Create a Lawyer
    try:
        lawyer_user = User.objects.get(email='lawyer.demo@lexregis.local')
        created = False
    except User.DoesNotExist:
        lawyer_user = User.objects.create_user(
            email='lawyer.demo@lexregis.local',
            password='password123',
            first_name='Harvey',
            last_name='Specter',
            role=RoleChoices.ADVOCATE
        )
        created = True

    lawyer_prof, _ = ProfessionalProfile.objects.get_or_create(
        user=lawyer_user,
        defaults={
            'designation': 'Senior Partner',
            'law_firm': 'Pearson Specter Litt',
            'years_of_experience': 20,
            'practice_areas': ['Corporate', 'Litigation'],
        }
    )
    print("Lawyer created/retrieved.")

    # 2. Create a Client
    try:
        client_user = User.objects.get(email='client.demo@lexregis.local')
        created = False
    except User.DoesNotExist:
        client_user = User.objects.create_user(
            email='client.demo@lexregis.local',
            password='password123',
            first_name='Mike',
            last_name='Ross',
            role=getattr(RoleChoices, 'CLIENT', 'CLIENT')
        )
        created = True

    client_profile, _ = Profile.objects.get_or_create(
        user=client_user,
        defaults={
            'city': 'New York',
            'client_type': 'INDIVIDUAL'
        }
    )
    print("Client created/retrieved.")

    # 3. Create a Case
    demo_case, created = Case.objects.get_or_create(
        title="Pearson vs Hardman Corporate Dispute",
        client=client_profile,
        defaults={
            'description': "A high stakes corporate dispute requiring immediate attention.",
            'assigned_lawyer': lawyer_prof,
            'status': CaseStatus.LAWYER_ASSIGNED,
            'practice_area': 'Corporate Litigation'
        }
    )
    if not created and not demo_case.assigned_lawyer:
        demo_case.assigned_lawyer = lawyer_prof
        demo_case.save()
    print("Case created/retrieved.")

    # 4. Create Conversation
    conversation, conv_created = Conversation.objects.get_or_create(
        case=demo_case,
        defaults={
            'status': ConversationStatus.ACTIVE
        }
    )
    
    if conv_created or conversation.participants.count() == 0:
        conversation.participants.add(client_user, lawyer_user)
        print("Conversation created and participants added.")

    # 5. Add Messages
    if not Message.objects.filter(conversation=conversation).exists():
        now = timezone.now()
        Message.objects.create(
            conversation=conversation,
            sender=client_user,
            content="Hi Harvey, I need your help with the Hardman situation. It's getting out of hand.",
            created_at=now - timedelta(hours=2)
        )
        Message.objects.create(
            conversation=conversation,
            sender=lawyer_user,
            content="I've looked at the files. We have them cornered on the embezzlement clause. Let's meet tomorrow.",
            created_at=now - timedelta(hours=1, minutes=45)
        )
        Message.objects.create(
            conversation=conversation,
            sender=client_user,
            content="Perfect. I'll bring the original contracts.",
            created_at=now - timedelta(hours=1, minutes=30)
        )
        
        # update the conversation last_message_at
        conversation.last_message_at = now - timedelta(hours=1, minutes=30)
        conversation.save()
        print("Demo messages seeded.")
    else:
        print("Messages already exist in this conversation.")

    print("Demo seeding completed successfully! You can login with:")
    print("Lawyer: lawyer.demo@lexregis.local / password123")
    print("Client: client.demo@lexregis.local / password123")

if __name__ == '__main__':
    seed_demo_data()
