import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import User
from apps.lawyer_portal.models import LawyerProfile
from apps.common.choices.system import RoleChoices

# Create Lawyer
lawyer_user, created = User.objects.get_or_create(email='lawyer@test.com', defaults={
    'first_name': 'Test',
    'last_name': 'Lawyer',
    'role': RoleChoices.ADVOCATE,
    'is_staff': False,
    'is_superuser': False,
    'phone_number': '1234567890'
})
if created:
    lawyer_user.set_password('password123')
    lawyer_user.save()

profile, created = LawyerProfile.objects.get_or_create(user=lawyer_user, defaults={
    'bar_council_number': 'MAH/123/2010',
    'years_of_experience': 10,
    'designation': 'Senior Advocate',
})

print(f"Lawyer seeded: {lawyer_user.email} / password123")
