from apps.analytics.services import AnalyticsService

class NationalAnalyticsPresenter:
    def __init__(self):
        self.service = AnalyticsService()

    def build_view_model(self):
        overview = self.service.get_national_overview()
        
        return {
            'overview': overview,
            'states': self.service.get_state_distribution(),
            'monthly_growth': self.service.get_monthly_growth(),
            'court_distribution': self.service.get_court_distribution(),
            'category_distribution': self.service.get_category_distribution()
        }

class StateAnalyticsPresenter:
    def __init__(self, slug):
        self.slug = slug
        self.service = AnalyticsService()
        
    def build_view_model(self):
        return {
            'state_name': self.slug.replace('-', ' ').title(),
            'overview': self.service.get_national_overview(), # Use scaled down version in real implementation
            'monthly_growth': self.service.get_monthly_growth(),
            'category_distribution': self.service.get_category_distribution()
        }

class AIAnalyticsPresenter:
    def __init__(self):
        self.service = AnalyticsService()
        
    def build_view_model(self):
        return self.service.get_ai_stats()

class BlockchainAnalyticsPresenter:
    def __init__(self):
        self.service = AnalyticsService()
        
    def build_view_model(self):
        return self.service.get_blockchain_stats()
