import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User, ProfessionalProfile
from apps.common.choices.system import RoleChoices

lawyers_data = [
    {
        "first_name": "Arvind",
        "last_name": "Narayanan",
        "email": "arvind.n@example.com",
        "designation": "Senior Advocate",
        "law_firm": "Narayanan & Associates",
        "office_address": "High Court, Delhi",
        "years_of_experience": 15,
        "practice_areas": ["Labour & Employment", "Corporate Litigation"],
    },
    {
        "first_name": "Priya",
        "last_name": "Sharma",
        "email": "priya.sharma@example.com",
        "designation": "Advocate",
        "law_firm": "Sharma Legal Chamber",
        "office_address": "Supreme Court, New Delhi",
        "years_of_experience": 8,
        "practice_areas": ["Civil Suits", "Family Law", "Labour & Employment"],
    },
    {
        "first_name": "Rajesh",
        "last_name": "Iyer",
        "email": "rajesh.iyer@example.com",
        "designation": "Managing Partner",
        "law_firm": "Iyer & Co.",
        "office_address": "Bombay High Court, Mumbai",
        "years_of_experience": 22,
        "practice_areas": ["Corporate Litigation", "Arbitration"],
    },
    {
        "first_name": "Meera",
        "last_name": "Desai",
        "email": "meera.desai@example.com",
        "designation": "Advocate",
        "law_firm": "Desai Legal",
        "office_address": "Pune District Court",
        "years_of_experience": 5,
        "practice_areas": ["Labour & Employment"],
    }
]

for data in lawyers_data:
    try:
        user = User.objects.get(email=data['email'])
        created = False
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=data['email'],
            password='password123',
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=RoleChoices.ADVOCATE
        )
        created = True

    prof, p_created = ProfessionalProfile.objects.get_or_create(
        user=user,
        defaults={
            'designation': data['designation'],
            'law_firm': data['law_firm'],
            'office_address': data['office_address'],
            'years_of_experience': data['years_of_experience'],
            'practice_areas': data['practice_areas'],
            'bar_council_number': f"MAH/{user.id}/2000"
        }
    )
    print(f"Lawyer {user.first_name} {user.last_name} created or exists.")
