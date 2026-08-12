from apps.cases.models.case import Case, CaseStatus, MatterSource
from apps.cases.models.timeline import CaseTimeline
from apps.accounts.models import Profile, ProfessionalProfile, User
from django.db import transaction
from django.utils import timezone

import json

import json
import uuid

class CaseCreationService:
    @staticmethod
    @transaction.atomic
    def create_case(data, files, user):
        extended_data = json.loads(data.get('extended_data', '{}'))
        
        # Handle Client
        client_mode = data.get('client_mode', 'existing')
        if client_mode == 'existing' and extended_data.get('client_id'):
            client = Profile.objects.get(id=extended_data.get('client_id'))
        else:
            email = extended_data.get('client_email', 'temp@example.com')
            name = extended_data.get('client_name', 'Client')
            new_user, _ = User.objects.get_or_create(
                email=email,
                defaults={'first_name': name}
            )
            client, _ = Profile.objects.get_or_create(user=new_user)
            client.address = extended_data.get('address')
            client.save()

        # Handle Assigned Lawyer
        lawyer_id = extended_data.get('assigned_lawyer_id')
        lawyer = ProfessionalProfile.objects.filter(id=lawyer_id).first() if lawyer_id else None
        
        # Determine location
        country = extended_data.get('country', '')
        state = extended_data.get('state', '')
        district = extended_data.get('district', '')
        city = extended_data.get('city', '')
        location_parts = [p for p in [city, district, state, country] if p]
        location_str = ", ".join(location_parts)
        
        # Priority and Urgency
        priority = extended_data.get('priority', '')
        if not priority:
            priority = extended_data.get('urgency', '')

        # Build Description with Extended Intake Data
        base_desc = extended_data.get('description', '')
        extra_info = []
        extra_info.append(f"Tags: {extended_data.get('tags', 'N/A')}")
        extra_info.append(f"Matter Type: {extended_data.get('matter_type', 'N/A')}")
        extra_info.append(f"Language: {extended_data.get('matter_language', 'N/A')}")
        extra_info.append(f"Source: {extended_data.get('source', 'Walk-in')}")
        extra_info.append(f"Confidential: {extended_data.get('confidential', 'No')}")
        
        # Client extended
        if client_mode == 'new':
            extra_info.append(f"\n--- CLIENT DETAILS ---")
            extra_info.append(f"Age/DOB: {extended_data.get('client_age', '')} / {extended_data.get('client_dob', '')}")
            extra_info.append(f"Occupation: {extended_data.get('client_occupation', '')}")
            extra_info.append(f"Alt Mobile: {extended_data.get('client_alt_mobile', '')}")
            extra_info.append(f"Aadhaar: {extended_data.get('client_aadhaar', '')}")
            extra_info.append(f"PAN: {extended_data.get('client_pan', '')}")
            extra_info.append(f"Emergency Contact: {extended_data.get('emergency_contact', '')} ({extended_data.get('emergency_relation', '')}) - {extended_data.get('emergency_mobile', '')}")
            extra_info.append(f"Client Notes: {extended_data.get('client_notes', '')}")

        # Opponents
        opponents = extended_data.get('opponents', [])
        if opponents:
            extra_info.append(f"\n--- OPPOSITE PARTIES ---")
            for idx, opp in enumerate(opponents, 1):
                extra_info.append(f"[{idx}] {opp.get('name')} ({opp.get('type')}) - {opp.get('relationship')}")
                if opp.get('advocate'):
                    extra_info.append(f"    Counsel: {opp.get('advocate')} ({opp.get('advocate_org', '')})")
                if opp.get('email') or opp.get('phone'):
                    extra_info.append(f"    Contact: {opp.get('email', '')} | {opp.get('phone', '')}")
                if opp.get('address'):
                    extra_info.append(f"    Address: {opp.get('address')}")
                if opp.get('assets') or opp.get('prior_cases'):
                    extra_info.append(f"    Assets/Cases: {opp.get('assets', 'None')} | {opp.get('prior_cases', 'None')}")
                if opp.get('remarks'):
                    extra_info.append(f"    Remarks: {opp.get('remarks')}")

        if extended_data.get('acts'):
            extra_info.append(f"\n--- LEGAL DETAILS ---")
            extra_info.append(f"Incident Time: {extended_data.get('incident_time')}")
            extra_info.append(f"Incident Location: {extended_data.get('incident_location')}")
            extra_info.append(f"Police Station: {extended_data.get('police_station')}")
            extra_info.append(f"Jurisdiction: {extended_data.get('jurisdiction')}")
            extra_info.append(f"Court Level: {extended_data.get('court_level')}")
            extra_info.append(f"Judge: {extended_data.get('judge_name')}")
            extra_info.append(f"Acts/Sections: {extended_data.get('acts')} / {extended_data.get('sections')}")
            extra_info.append(f"FIR Number: {extended_data.get('fir_number')}")
            extra_info.append(f"Charge Sheet: {extended_data.get('charge_sheet')}")
            extra_info.append(f"Reference Number: {extended_data.get('reference_number')}")
            extra_info.append(f"Current Stage: {extended_data.get('current_stage')}")
            extra_info.append(f"Relief Sought: {extended_data.get('relief_sought')}")
            extra_info.append(f"Expected Outcome: {extended_data.get('expected_outcome')}")
            extra_info.append(f"Prev Litigation: {extended_data.get('prev_litigation')}")
            extra_info.append(f"Notice Issued: {extended_data.get('notice_issued')}")
            extra_info.append(f"Limitation Period: {extended_data.get('limitation_period')}")

        if extended_data.get('retainer_fee') or extended_data.get('consultation_fee'):
            extra_info.append(f"\n--- FINANCIALS ---")
            extra_info.append(f"Consultation Fee: {extended_data.get('consultation_fee')}")
            extra_info.append(f"Retainer Fee: {extended_data.get('retainer_fee')}")
            extra_info.append(f"Court Fee: {extended_data.get('court_fee')}")
            extra_info.append(f"Govt/Stamp Duty: {extended_data.get('govt_fee')}")
            extra_info.append(f"Discount: {extended_data.get('discount')}%")
            extra_info.append(f"GST: {extended_data.get('gst')}%")
            extra_info.append(f"Advance Paid: {extended_data.get('advance_paid')}")
            extra_info.append(f"Payment Method: {extended_data.get('payment_method')}")
            extra_info.append(f"Invoice Required: {extended_data.get('invoice_required')}")
            
        full_description = f"{base_desc}\n\n" + "\n".join(extra_info)

        # Main Opponent name for Case model field
        main_opponent = ''
        if opponents and opponents[0].get('name'):
            main_opponent = opponents[0].get('name')

        # 3. Create Case
        case = Case.objects.create(
            title=extended_data.get('title', 'Untitled Case'),
            description=full_description,
            client=client,
            assigned_lawyer=lawyer,
            matter_category=extended_data.get('matter_category', ''),
            practice_area=extended_data.get('practice_area', ''),
            sub_category=extended_data.get('sub_category', ''),
            complexity=extended_data.get('complexity', ''),
            timeline_estimate=extended_data.get('timeline_estimate', ''),
            budget_estimate=extended_data.get('budget_estimate') or None,
            case_value=extended_data.get('case_value') or None,
            priority=priority,
            court=extended_data.get('court', ''),
            location=location_str,
            status=CaseStatus.DRAFT if data.get('action') == 'save_draft' else CaseStatus.PENDING_ACCEPTANCE,
            matter_source=MatterSource.MANUAL,
            incident_date=extended_data.get('incident_date') or None,
            opponent_name=main_opponent
        )

        # 4. Handle Hearings
        hearing_date = extended_data.get('hearing_date')
        if hearing_date:
            from apps.hearings.models import Hearing, HearingStatus, HearingType
            
            # Use defaults if tables aren't pre-populated
            h_status, _ = HearingStatus.objects.get_or_create(code='SCHEDULED', defaults={'name': 'Scheduled'})
            h_type, _ = HearingType.objects.get_or_create(code='FIRST_HEARING', defaults={'name': 'First Hearing'})
            
            # Time defaults to 10:00 AM if not provided
            hearing_time_str = extended_data.get('hearing_time')
            if not hearing_time_str:
                hearing_time_str = "10:00:00"
                
            Hearing.objects.create(
                hearing_number=f"HRG-{uuid.uuid4().hex[:8].upper()}",
                case=case,
                hearing_type=h_type,
                status=h_status,
                scheduled_date=hearing_date,
                scheduled_time=hearing_time_str,
                hearing_outcome=f"Mode: {extended_data.get('hearing_mode')} | Court: {extended_data.get('hearing_court', 'TBD')} | Judge: {extended_data.get('hearing_judge', 'TBD')} | Notes: {extended_data.get('hearing_notes', '')}"
            )

        # 5. Handle Documents
        for f in files.getlist('documents'):
            from apps.documents.models import Document
            Document.objects.create(
                document_number=f"DOC-{case.id}-{timezone.now().timestamp()}",
                case=case,
                uploaded_by=user,
                owner=user,
                original_file=f,
            )

        # 6. Timeline
        CaseTimeline.objects.create(
            case=case,
            event_code='CREATED',
            event_category='LIFECYCLE',
            description=f'Enterprise Case {case.case_number} was created by {user.get_full_name()}',
            actor=user
        )

        return case
