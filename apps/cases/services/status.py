from apps.cases.models import CaseStatusHistory, CaseTimeline

class CaseStatusService:
    @staticmethod
    def change_status(case, new_status, changed_by, remarks=""):
        old_status = case.status
        if old_status == new_status:
            return None
            
        case.status = new_status
        case.save(update_fields=['status', 'updated_at'])
        
        history = CaseStatusHistory.objects.create(
            case=case,
            previous_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks
        )
        
        CaseTimeline.objects.create(
            case=case,
            performed_by=changed_by,
            event_type='STATUS_CHANGED',
            description=f'Status changed from {old_status} to {new_status}'
        )
        return history
