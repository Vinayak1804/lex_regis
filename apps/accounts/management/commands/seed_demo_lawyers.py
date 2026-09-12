from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.accounts.models import Profile, ProfessionalProfile

User = get_user_model()

DEMO_LAWYERS = [
    {
        'first_name': 'Demo',
        'last_name': 'Sanjay Joshi',
        'email': 'sanjay.joshi.demo@lexregis.local',
        'designation': 'Senior Advocate',
        'years_of_experience': 15,
        'city': 'Mumbai',
        'practice_areas': ['Civil Litigation', 'Property Law', 'Consumer Law'],
        'short_bio': 'Experienced in civil disputes and property matters across Mumbai.'
    },
    {
        'first_name': 'Demo',
        'last_name': 'Priya Sharma',
        'email': 'priya.sharma.demo@lexregis.local',
        'designation': 'Advocate',
        'years_of_experience': 8,
        'city': 'Delhi',
        'practice_areas': ['Family Law', 'Corporate Law'],
        'short_bio': 'Specialized in family disputes and corporate compliance.'
    },
    {
        'first_name': 'Demo',
        'last_name': 'Rahul Verma',
        'email': 'rahul.verma.demo@lexregis.local',
        'designation': 'Advocate',
        'years_of_experience': 5,
        'city': 'Bangalore',
        'practice_areas': ['Cyber Law', 'Intellectual Property'],
        'short_bio': 'Focuses on IP rights and cyber crimes.'
    },
    {
        'first_name': 'Demo',
        'last_name': 'Anita Desai',
        'email': 'anita.desai.demo@lexregis.local',
        'designation': 'Senior Advocate',
        'years_of_experience': 22,
        'city': 'Chennai',
        'practice_areas': ['Taxation', 'Corporate Law'],
        'short_bio': 'Expert in corporate taxation and mergers.'
    },
    {
        'first_name': 'Demo',
        'last_name': 'Vikram Singh',
        'email': 'vikram.singh.demo@lexregis.local',
        'designation': 'Advocate',
        'years_of_experience': 12,
        'city': 'Hyderabad',
        'practice_areas': ['Criminal Law', 'Civil Litigation'],
        'short_bio': 'Handles complex criminal defense cases.'
    },
    {
        'first_name': 'Demo',
        'last_name': 'Meera Reddy',
        'email': 'meera.reddy.demo@lexregis.local',
        'designation': 'Advocate',
        'years_of_experience': 7,
        'city': 'Pune',
        'practice_areas': ['Labour & Employment', 'Consumer Law'],
        'short_bio': 'Passionate about workers rights and consumer protection.'
    }
]

class Command(BaseCommand):
    help = 'Seeds the database with demo lawyers and a demo client'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding demo users...')
        password = 'demopassword123'
        
        # Create Demo Client
        client_email = 'client.demo@lexregis.local'
        try:
            client_user = User.objects.get(email=client_email)
            self.stdout.write(f'Demo Client already exists: {client_email}')
        except User.DoesNotExist:
            client_user = User.objects.create_user(
                email=client_email,
                password=password,
                first_name='Demo',
                last_name='Client',
                role='CLIENT'
            )
            profile = client_user.profile
            profile.city = 'Mumbai'
            profile.client_type = 'INDIVIDUAL'
            profile.save()
            self.stdout.write(f'Created Demo Client: {client_email} / {password}')
            
        for data in DEMO_LAWYERS:
            try:
                user = User.objects.get(email=data['email'])
                self.stdout.write(f'Demo Lawyer already exists: {data["email"]}')
            except User.DoesNotExist:
                user = User.objects.create_user(
                    email=data['email'],
                    password=password,
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    role='ADVOCATE'
                )
                
                # Profile
                profile = user.profile
                profile.city = data['city']
                profile.short_bio = data['short_bio']
                profile.save()
                
                # Professional Profile
                prof_profile = user.professional_profile
                prof_profile.designation = data['designation']
                prof_profile.years_of_experience = data['years_of_experience']
                prof_profile.practice_areas = data['practice_areas']
                prof_profile.save()
                self.stdout.write(f'Created Demo Lawyer: {data["email"]} / {password}')
            else:
                self.stdout.write(f'Demo Lawyer already exists: {data["email"]}')
                
        self.stdout.write(self.style.SUCCESS('Successfully seeded demo users!'))
