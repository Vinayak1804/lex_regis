class DomainEventService:
    @staticmethod
    def publish_hearing_scheduled(hearing):
        """
        Publish event when a new hearing is scheduled.
        Listeners: NotificationService, AnalyticsService, CalendarService.
        """
        pass

    @staticmethod
    def publish_hearing_rescheduled(hearing, old_date, new_date):
        """
        Publish event when a hearing is rescheduled.
        """
        pass

    @staticmethod
    def publish_hearing_completed(hearing):
        """
        Publish event when a hearing completes.
        Listeners: MLPredictionService (to update outcome), BlockchainService (to store hash).
        """
        pass

    @staticmethod
    def publish_adjournment_requested(adjournment):
        pass
        
    @staticmethod
    def publish_adjournment_granted(adjournment):
        pass
