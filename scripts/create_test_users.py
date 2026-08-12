import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth import get_user_model
from apps.accounts.models import Profile, ProfessionalProfile

User = get_user_model()

# Create or update Client
client_user, created = User.objects.get_or_create(
    email='client@example.com',
    defaults={
        'first_name': 'Test',
        'last_name': 'Client',
        'role': 'CLIENT',
        'is_active': True,
        'password': 'temp'
    }
)
client_user.set_password('password123')
client_user.save()
Profile.objects.get_or_create(user=client_user)

# Create or update Lawyer
lawyer_user, created = User.objects.get_or_create(
    email='arvind.n@example.com',
    defaults={
        'first_name': 'Arvind',
        'last_name': 'Natarajan',
        'role': 'ADVOCATE',
        'is_active': True,
        'password': 'temp'
    }
)
lawyer_user.set_password('password123')
lawyer_user.save()
ProfessionalProfile.objects.get_or_create(user=lawyer_user)

# Create or update Admin
admin_user, created = User.objects.get_or_create(
    email='admin@example.com',
    defaults={
        'first_name': 'System',
        'last_name': 'Admin',
        'role': 'ADMIN',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True,
        'password': 'temp'
    }
)
admin_user.set_password('password123')
admin_user.save()

print("Test users successfully created/updated!")
