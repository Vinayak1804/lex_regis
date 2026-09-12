from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.cases.models import Case
from apps.ml.services.feature_extraction import extract_historical_features
from apps.ml.services.embedding_service import embed_case_feature
from datetime import timedelta
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds synthetic historical cases for testing similarity retrieval'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding historical cases...")
        
        # Ensure we have a profile and user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No users found in database. Create a user first."))
            return
        from apps.accounts.models import Profile
        profile, _ = Profile.objects.get_or_create(user=user)
            
        cases_data = [
            {
                "title": "State vs. ABC Corp - Contract Dispute",
                "matter_category": "Civil",
                "location": "Maharashtra",
                "description": "Breach of contract regarding the supply of raw materials to the state manufacturing facility. The defendant failed to deliver on time causing massive losses.",
                "status": "CLOSED",
            },
            {
                "title": "XYZ Pvt Ltd vs. Union of India",
                "matter_category": "Taxation",
                "location": "Delhi",
                "description": "Dispute over GST classification of software licenses. The company claims it should be taxed at 5% instead of 18%.",
                "status": "CLOSED",
            },
            {
                "title": "Employee vs. Tech Startup",
                "matter_category": "Labor",
                "location": "Karnataka",
                "description": "Wrongful termination of an employee without prior notice. The employee claims back pay and damages for mental harassment.",
                "status": "CLOSED",
            },
            {
                "title": "Ramesh vs. Suresh Property Dispute",
                "matter_category": "Civil",
                "location": "Maharashtra",
                "description": "Family property dispute over the division of ancestral land in Pune. Involves forged documents.",
                "status": "CLOSED",
            },
            {
                "title": "Software Copyright Infringement",
                "matter_category": "Intellectual Property",
                "location": "Karnataka",
                "description": "A former employee stole proprietary source code and started a competing SaaS business.",
                "status": "CLOSED",
            }
        ]
        
        for data in cases_data:
            case, created = Case.objects.get_or_create(
                title=data['title'],
                client=profile,
                defaults={
                    'matter_category': data['matter_category'],
                    'location': data['location'],
                    'description': data['description'],
                    'status': data['status'],
                    'court': 'Demo Court',
                }
            )
            
            # Extract historical features
            feature = extract_historical_features(case, is_synthetic=True)
            embed_case_feature(feature)
            
            self.stdout.write(self.style.SUCCESS(f"Processed: {case.title}"))
            
        self.stdout.write(self.style.SUCCESS("Demo case history seeded and embedded successfully!"))
