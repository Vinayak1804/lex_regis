from apps.cases.models.master import CaseStatus

class CaseWorkflowService:
    VALID_TRANSITIONS = {
        'DRAFT': ['FILED'],
        'FILED': ['UNDER_REVIEW', 'REJECTED'],
        'UNDER_REVIEW': ['EVIDENCE', 'REJECTED'],
        'EVIDENCE': ['ARGUMENTS'],
        'ARGUMENTS': ['JUDGMENT_RESERVED'],
        'JUDGMENT_RESERVED': ['CLOSED', 'COMPLETED'],
        'COMPLETED': ['APPEALED', 'CLOSED'],
        'REJECTED': ['CLOSED'],
        'APPEALED': ['IN_PROGRESS'],
    }

    @staticmethod
    def can_transition(current_status_code, next_status_code):
        allowed = CaseWorkflowService.VALID_TRANSITIONS.get(current_status_code, [])
        return next_status_code in allowed
