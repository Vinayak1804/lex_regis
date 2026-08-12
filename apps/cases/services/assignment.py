from apps.cases.models import CaseAssignment, CaseTimeline

class CaseAssignmentService:
    @staticmethod
    def assign_lawyer(case, lawyer, assigned_by, notes=""):
        assignment = CaseAssignment.objects.create(
            case=case,
            assigned_lawyer=lawyer,
            assigned_by=assigned_by,
            assignment_notes=notes
        )
        case.assigned_lawyer = lawyer
        case.save(update_fields=['assigned_lawyer', 'updated_at'])
        
        CaseTimeline.objects.create(
            case=case,
            performed_by=assigned_by,
            event_type='LAWYER_ASSIGNED',
            description=f'Lawyer {lawyer} assigned to case.'
        )
        return assignment
