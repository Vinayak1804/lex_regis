class DemoDataProvider:
    @staticmethod
    def get_national_overview():
        return {
            'total_cases': 248931,
            'pending_cases': 91384,
            'disposed_cases': 157547,
            'active_advocates': 12450,
            'registered_clients': 85300,
            'total_hearings': 1054230,
            'documents_uploaded': 3567890,
            'blockchain_verified': 2854300,
            'ai_assisted': 45210,
            'total_law_firms': 850
        }

    @staticmethod
    def get_state_distribution():
        # Tele-law style data for major states
        return [
            {'state': 'Uttar Pradesh', 'total': 2074144, 'pending': 725000, 'disposed': 1349144, 'advocates': 2450, 'slug': 'uttar-pradesh'},
            {'state': 'Maharashtra', 'total': 1233939, 'pending': 450000, 'disposed': 783939, 'advocates': 1800, 'slug': 'maharashtra'},
            {'state': 'Jammu And Kashmir', 'total': 773478, 'pending': 220000, 'disposed': 553478, 'advocates': 450, 'slug': 'jammu-and-kashmir'},
            {'state': 'Bihar', 'total': 648125, 'pending': 310000, 'disposed': 338125, 'advocates': 890, 'slug': 'bihar'},
            {'state': 'Madhya Pradesh', 'total': 935920, 'pending': 410000, 'disposed': 525920, 'advocates': 1100, 'slug': 'madhya-pradesh'},
            {'state': 'Rajasthan', 'total': 671976, 'pending': 295000, 'disposed': 376976, 'advocates': 780, 'slug': 'rajasthan'},
            {'state': 'Karnataka', 'total': 565711, 'pending': 245000, 'disposed': 320711, 'advocates': 950, 'slug': 'karnataka'},
            {'state': 'Gujarat', 'total': 490226, 'pending': 195000, 'disposed': 295226, 'advocates': 820, 'slug': 'gujarat'},
            {'state': 'Jharkhand', 'total': 491023, 'pending': 185000, 'disposed': 306023, 'advocates': 600, 'slug': 'jharkhand'},
            {'state': 'Odisha', 'total': 415564, 'pending': 165000, 'disposed': 250564, 'advocates': 550, 'slug': 'odisha'},
            {'state': 'Andhra Pradesh', 'total': 388628, 'pending': 145000, 'disposed': 243628, 'advocates': 680, 'slug': 'andhra-pradesh'},
            {'state': 'Telangana', 'total': 317330, 'pending': 125000, 'disposed': 192330, 'advocates': 700, 'slug': 'telangana'},
            {'state': 'Tamil Nadu', 'total': 306922, 'pending': 135000, 'disposed': 171922, 'advocates': 980, 'slug': 'tamil-nadu'},
            {'state': 'West Bengal', 'total': 272994, 'pending': 115000, 'disposed': 157994, 'advocates': 850, 'slug': 'west-bengal'},
        ]

    @staticmethod
    def get_monthly_growth():
        return {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'cases': [12500, 14200, 18500, 21000, 24500, 22100, 25800, 28900, 31200, 34500, 38100, 42000],
            'disposals': [9500, 10200, 14500, 16000, 18500, 17100, 21800, 23900, 26200, 29500, 32100, 35000]
        }

    @staticmethod
    def get_court_distribution():
        return {
            'labels': ['Supreme Court', 'High Courts', 'District Courts', 'Family Courts', 'Tribunals', 'Consumer Courts'],
            'data': [85000, 6200000, 42500000, 1500000, 2100000, 1800000]
        }
        
    @staticmethod
    def get_category_distribution():
        return {
            'labels': ['Civil', 'Criminal', 'Corporate', 'Family', 'Property', 'Constitutional'],
            'data': [45, 30, 10, 8, 5, 2]
        }

    @staticmethod
    def get_ai_stats():
        return {
            'total_queries': 125430,
            'documents_summarized': 45890,
            'contracts_reviewed': 12300,
            'predictions_generated': 8450,
            'avg_response_time': '1.2s',
            'daily_usage': [450, 520, 610, 780, 850, 920, 1050],
            'monthly_usage': [12000, 14500, 18200, 24000, 32000, 41000]
        }

    @staticmethod
    def get_blockchain_stats():
        return {
            'verified_documents': 2854300,
            'verification_requests': 14500,
            'network_status': 'Healthy',
            'verification_time': '2.4s',
            'daily': [1200, 1450, 1600, 1850, 2100, 2400, 2800],
            'monthly': [45000, 52000, 61000, 78000, 95000, 115000]
        }
