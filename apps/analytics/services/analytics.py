from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from apps.cases.models import Case
from apps.documents.models import Document
from apps.hearings.models import Hearing
from apps.accounts.models import ProfessionalProfile, Organization, User
from .demo_data import DemoDataProvider

class AnalyticsService:
    @staticmethod
    def get_national_overview():
        total_cases = Case.objects.count()
        
        if total_cases < 100:
            return DemoDataProvider.get_national_overview()
            
        from apps.cases.models.case import CaseStatus
        return {
            'total_cases': total_cases,
            'pending_cases': Case.objects.filter(status__in=[CaseStatus.FILED, CaseStatus.HEARINGS]).count(),
            'disposed_cases': Case.objects.filter(status__in=[CaseStatus.CLOSED, CaseStatus.ARCHIVED]).count(),
            'active_advocates': ProfessionalProfile.objects.count(),
            'registered_clients': User.objects.filter(role='CLIENT').count(),
            'total_hearings': Hearing.objects.count(),
            'documents_uploaded': Document.objects.count(),
            'blockchain_verified': Document.objects.filter(is_verified_on_blockchain=True).count(),
            'ai_assisted': Case.objects.filter(ai_insights__isnull=False).distinct().count(),
            'total_law_firms': Organization.objects.count()
        }

    @staticmethod
    def get_state_distribution():
        total_cases = Case.objects.count()
        if total_cases < 100:
            return DemoDataProvider.get_state_distribution()
            
        # Real query would aggregate by Court's state if we had a state field.
        # Assuming Court model has a state field, but we'll use demo data structure fallback.
        return DemoDataProvider.get_state_distribution()
        
    @staticmethod
    def get_monthly_growth():
        total_cases = Case.objects.count()
        if total_cases < 100:
            return DemoDataProvider.get_monthly_growth()
        return DemoDataProvider.get_monthly_growth()

    @staticmethod
    def get_court_distribution():
        total_cases = Case.objects.count()
        if total_cases < 100:
            return DemoDataProvider.get_court_distribution()
        return DemoDataProvider.get_court_distribution()
        
    @staticmethod
    def get_category_distribution():
        total_cases = Case.objects.count()
        if total_cases < 100:
            return DemoDataProvider.get_category_distribution()
        return DemoDataProvider.get_category_distribution()

    @staticmethod
    def get_ai_stats():
        return DemoDataProvider.get_ai_stats()
        
    @staticmethod
    def get_blockchain_stats():
        return DemoDataProvider.get_blockchain_stats()
