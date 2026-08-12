from apps.dashboard.services.dashboard import DashboardService

class DashboardPresenter:
    def __init__(self, user):
        self.service = DashboardService(user)
        
    def build_view_model(self):
        data = self.service.get_dashboard_data()
        
        # Formatting for UI
        return {
            'stats': [
                {'title': 'Total Cases', 'value': data['total_cases'], 'icon': 'briefcase', 'color': 'primary', 'trend': '12%'},
                {'title': 'Open Cases', 'value': data['open_cases'], 'icon': 'folder-open', 'color': 'success', 'trend': '8%'},
                {'title': 'Pending Cases', 'value': data['pending_cases'], 'icon': 'clock-rotate-left', 'color': 'warning', 'trend': '5%'},
                {'title': 'Closed Cases', 'value': data['closed_cases'], 'icon': 'check-circle', 'color': 'secondary', 'trend': '15%'},
            ],
            'recent_cases': data['recent_cases'],
            'upcoming_hearings': data['upcoming_hearings'],
            'recent_documents': data['recent_documents'],
            'activity_feed': data['activity_feed'],
            'ai_ready': True,
            'blockchain_ready': True
        }
