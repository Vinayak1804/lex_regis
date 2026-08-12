class DashboardStatisticsService:
    @staticmethod
    def get_total_cases(user):
        from apps.cases.models import Case
        return Case.objects.count()

    @staticmethod
    def get_open_cases_count(user):
        from apps.cases.models import Case
        from apps.cases.models.case import CaseStatus
        return Case.objects.exclude(status__in=[CaseStatus.CLOSED, CaseStatus.ARCHIVED, CaseStatus.DRAFT]).count()
        
    @staticmethod
    def get_pending_cases_count(user):
        from apps.cases.models import Case
        from apps.cases.models.case import CaseStatus
        return Case.objects.filter(status=CaseStatus.PENDING_ACCEPTANCE).count()
        
    @staticmethod
    def get_closed_cases_count(user):
        from apps.cases.models import Case
        from apps.cases.models.case import CaseStatus
        return Case.objects.filter(status=CaseStatus.CLOSED).count()
    
    @staticmethod
    def get_pending_hearings_count(user):
        from apps.hearings.models import Hearing
        return Hearing.objects.filter(status__code='SCHEDULED').count()
        
    @staticmethod
    def get_total_documents_count(user):
        from apps.documents.models import Document
        return Document.objects.filter(is_active=True).count()
    
    @staticmethod
    def get_unread_notifications_count(user):
        from apps.notifications.models import Notification
        return Notification.objects.filter(user=user, is_read=False).count()

class DashboardWidgetService:
    @staticmethod
    def get_recent_cases(user, limit=5):
        from apps.cases.models import Case
        return Case.objects.select_related('assigned_lawyer').order_by('-created_at')[:limit]
        
    @staticmethod
    def get_upcoming_hearings(user, limit=5):
        from apps.hearings.models import Hearing
        return Hearing.objects.select_related('case', 'presiding_judge', 'court_room').filter(status__code='SCHEDULED').order_by('scheduled_date', 'scheduled_time')[:limit]

    @staticmethod
    def get_recent_documents(user, limit=5):
        from apps.documents.models import Document
        return Document.objects.select_related('case', 'uploaded_by').filter(is_active=True).order_by('-upload_timestamp')[:limit]
        
    @staticmethod
    def get_activity_feed(user, limit=10):
        from apps.cases.models import Case
        from apps.documents.models import Document
        from apps.hearings.models import Hearing
        
        # Build synthetic activity feed from recent objects
        cases = list(Case.objects.select_related('assigned_lawyer').order_by('-created_at')[:limit])
        docs = list(Document.objects.select_related('case', 'uploaded_by').order_by('-upload_timestamp')[:limit])
        
        feed = []
        for c in cases:
            feed.append({
                'title': f"New Case Opened: {c.title}",
                'timestamp': c.created_at,
                'type': 'case',
                'icon': 'fa-briefcase'
            })
        for d in docs:
            title = d.original_file.name if d.original_file else f"Doc {d.document_number}"
            feed.append({
                'title': f"Document Uploaded: {title}",
                'timestamp': d.upload_timestamp,
                'type': 'document',
                'icon': 'fa-file-contract'
            })
            
        feed.sort(key=lambda x: x['timestamp'], reverse=True)
        return feed[:limit]

class DashboardService:
    def __init__(self, user):
        self.user = user
        self.stats = DashboardStatisticsService()
        self.widgets = DashboardWidgetService()
        
    def get_dashboard_data(self):
        return {
            'total_cases': self.stats.get_total_cases(self.user),
            'open_cases': self.stats.get_open_cases_count(self.user),
            'pending_cases': self.stats.get_pending_cases_count(self.user),
            'closed_cases': self.stats.get_closed_cases_count(self.user),
            'active_cases': self.stats.get_open_cases_count(self.user), # Fallback for old templates
            'pending_hearings': self.stats.get_pending_hearings_count(self.user),
            'total_documents': self.stats.get_total_documents_count(self.user),
            'unread_notifications': self.stats.get_unread_notifications_count(self.user),
            'recent_cases': self.widgets.get_recent_cases(self.user),
            'upcoming_hearings': self.widgets.get_upcoming_hearings(self.user),
            'recent_documents': self.widgets.get_recent_documents(self.user),
            'activity_feed': self.widgets.get_activity_feed(self.user),
        }
