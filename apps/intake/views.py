from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from .models import LegalIssue, DocumentUpload, AIAnalysis, ConsultationRequest
from apps.ai.services.triage import AITriageService
from apps.ml.services.historical_context import HistoricalContextService
from apps.intake.services.matching import LawyerMatchService

class IntakeLandingView(TemplateView):
    template_name = 'intake/landing.html'

class LearnMoreView(TemplateView):
    template_name = 'intake/learn_more.html'

class IntakeWizardView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def get(self, request):
        return render(request, 'intake/ai_intake.html')

class TalkToLawyerWizardView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def get(self, request):
        return render(request, 'intake/talk_to_lawyer.html')
    
    def post(self, request):
        description = request.POST.get('description', '')
        category = request.POST.get('category', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        urgency = request.POST.get('urgency', 'ROUTINE')
        budget = request.POST.get('budget', '')
        preferred_consultation = request.POST.get('preferred_consultation', '')
        
        # New optional fields
        preferred_language = request.POST.get('preferred_language', '')
        best_time_to_consult = request.POST.get('best_time_to_consult', '')
        already_have_lawyer_str = request.POST.get('already_have_lawyer', '')
        hearing_scheduled_str = request.POST.get('hearing_scheduled', '')
        incident_date = request.POST.get('incident_date', None)
        
        already_have_lawyer = True if already_have_lawyer_str.lower() in ['true', 'yes', '1'] else False if already_have_lawyer_str.lower() in ['false', 'no', '0'] else None
        hearing_scheduled = True if hearing_scheduled_str.lower() in ['true', 'yes', '1'] else False if hearing_scheduled_str.lower() in ['false', 'no', '0'] else None
        
        if incident_date == '':
            incident_date = None
            
        extra_context = request.POST.get('extra_context', '')
        if extra_context:
            description = description + "\n" + extra_context
            
        issue = LegalIssue.objects.create(
            user=request.user,
            description=description,
            category=category,
            city=city,
            state=state,
            urgency=urgency,
            budget=budget,
            preferred_consultation=preferred_consultation,
            preferred_language=preferred_language,
            best_time_to_consult=best_time_to_consult,
            already_have_lawyer=already_have_lawyer,
            hearing_scheduled=hearing_scheduled,
            incident_date=incident_date,
            status='ANALYZED'
        )
        
        try:
            AITriageService.analyze_issue(issue)
        except Exception as e:
            messages.error(request, "AI Analysis is currently unavailable. Please proceed with basic processing.")
            
        return redirect(reverse('intake:triage_results', kwargs={'issue_id': issue.id}))

class TriageResultsView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def get(self, request, issue_id):
        try:
            issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        except LegalIssue.DoesNotExist:
            return redirect('public_site:home')
            
        analysis = getattr(issue, 'ai_analysis', None)
        
        if analysis:
            historical_cases = HistoricalContextService.get_similar_cases(issue, analysis)
            matched_lawyers = LawyerMatchService.get_matched_lawyers(issue, analysis)
        else:
            historical_cases = []
            matched_lawyers = []
            
        context = {
            'issue': issue,
            'analysis': analysis,
            'historical_cases': historical_cases,
            'matched_lawyers': matched_lawyers
        }
        return render(request, 'intake/triage_results.html', context)

class BookLawyerView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def post(self, request, issue_id):
        try:
            issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        except LegalIssue.DoesNotExist:
            return redirect('public_site:home')
            
        lawyer_id = request.POST.get('lawyer_id')
        from apps.accounts.models import ProfessionalProfile
        
        try:
            lawyer = ProfessionalProfile.objects.get(id=lawyer_id)
        except ProfessionalProfile.DoesNotExist:
            messages.error(request, "Lawyer not found.")
            return redirect(reverse('intake:triage_results', kwargs={'issue_id': issue.id}))
            
        # Prevent duplicate submissions
        existing_request = ConsultationRequest.objects.filter(
            issue=issue, 
            lawyer=lawyer
        ).first()
        
        if existing_request:
            return redirect(reverse('intake:consultation_status', kwargs={'request_id': existing_request.id}))
            
        # Create lightweight case
        from apps.cases.models.case import Case, CaseStatus, MatterSource
        ai = getattr(issue, 'ai_analysis', None)
        new_case = Case.objects.create(
            title=f"Lawyer Request: {(lawyer.user.first_name + ' ' + lawyer.user.last_name).strip()} - {issue.city}",
            description=issue.description,
            client=request.user.profile,
            assigned_lawyer=lawyer,
            matter_category=ai.category if ai else '',
            practice_area=ai.practice_area if ai else '',
            sub_category=ai.subcategory if ai else '',
            status=CaseStatus.PENDING_ACCEPTANCE,
            matter_source=MatterSource.TALK_TO_LAWYER,
            ai_analysis_id=ai.id if ai else None,
            location=issue.city
        )

        # Create Consultation Request
        cr = ConsultationRequest.objects.create(
            client=request.user,
            lawyer=lawyer,
            issue=issue,
            case=new_case,
            status=ConsultationRequest.StatusChoices.PENDING
        )
        
        # Notifications
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=lawyer.user,
            title="New Consultation Request",
            message=f"You have a new consultation request from {request.user.first_name}.",
            notification_type='LAWYER_ASSIGNMENT',
            target_url=reverse('lawyer_portal:dashboard')
        )
        
        Notification.objects.create(
            user=request.user,
            title="Consultation Requested",
            message=f"Your request has been sent to {lawyer.user.first_name}. You will be notified when they respond.",
            notification_type='CONSULTATION_SENT',
            target_url=reverse('intake:consultation_status', kwargs={'request_id': cr.id})
        )
        
        return redirect(reverse('intake:consultation_status', kwargs={'request_id': cr.id}))

class ClientConsultationStatusView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def get(self, request, request_id):
        try:
            consultation = ConsultationRequest.objects.get(id=request_id, client=request.user)
        except ConsultationRequest.DoesNotExist:
            return redirect('public_site:home')
            
        context = {
            'consultation': consultation
        }
        return render(request, 'intake/consultation_status.html', context)
        
class ConvertConsultationView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def post(self, request, request_id):
        from apps.cases.models.case import Case, CaseStatus, MatterSource
        from django.db import transaction
        from apps.communication.models import Conversation
        
        try:
            consultation = ConsultationRequest.objects.get(id=request_id)
        except ConsultationRequest.DoesNotExist:
            return redirect('dashboard:index')
            
        # Check authorization (Client or Lawyer involved)
        if request.user != consultation.client and request.user != consultation.lawyer.user:
            messages.error(request, "Unauthorized")
            return redirect('dashboard:index')
            
        if consultation.status != ConsultationRequest.StatusChoices.COMPLETED and consultation.status != ConsultationRequest.StatusChoices.ACTIVE:
            messages.error(request, "Consultation must be active or completed to convert.")
            return redirect(reverse('intake:consultation_status', kwargs={'request_id': consultation.id}))
            
        with transaction.atomic():
            ai = getattr(consultation.issue, 'ai_analysis', None)
            
            # Upgrade existing case or create if missing
            case = consultation.case
            if case:
                case.status = CaseStatus.ACTIVE
                case.title = f"{ai.subcategory if ai else 'Legal Matter'} - {consultation.issue.city or consultation.issue.district}"
                case.matter_category = ai.category if ai else ''
                case.practice_area = ai.practice_area if ai else ''
                # Keep matter_source as TALK_TO_LAWYER since it originated there
                case.save()
            else:
                case = Case.objects.create(
                    title=f"{ai.subcategory if ai else 'Legal Matter'} - {consultation.issue.city or consultation.issue.district}",
                    description=consultation.issue.description,
                    client=consultation.client.profile,
                    assigned_lawyer=consultation.lawyer,
                    matter_category=ai.category if ai else '',
                    practice_area=ai.practice_area if ai else '',
                    status=CaseStatus.ACTIVE,
                    matter_source=MatterSource.TALK_TO_LAWYER
                )
                consultation.case = case
                consultation.save()
            
            # Migrate Conversation
            conversation = Conversation.objects.filter(
                participants=consultation.client
            ).filter(participants=consultation.lawyer.user).first()
            
            if conversation:
                conversation.case = case
                conversation.save()
                
        messages.success(request, f"Consultation successfully converted to Case {case.case_number}.")
        if request.user == consultation.client:
            return redirect('dashboard:index')
        else:
            return redirect('lawyer_portal:dashboard')

class ConsultationChatbotAPIView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def post(self, request):
        import json
        from django.http import JsonResponse
        from django.conf import settings
        from groq import Groq
        from apps.ai.models import AIRequestLog
        
        try:
            data = json.loads(request.body)
            query = data.get('message', '')
            history = data.get('history', [])
            issue_id = data.get('issue_id', None)
            
            if not query:
                return JsonResponse({'error': 'Message is required'}, status=400)
                
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = "You are Lex AI, a highly advanced, professional, and knowledgeable legal assistant for the Lex Regis platform. You answer questions accurately, reference Indian Law context where applicable, and maintain a highly professional tone. You are currently assisting a user in a consultation intake phase."
            
            if issue_id:
                try:
                    issue = LegalIssue.objects.get(id=issue_id, user=request.user)
                    ai_analysis = getattr(issue, 'ai_analysis', None)
                    system_prompt += f"\n\nUser's Intake Description:\n{issue.description}"
                    if ai_analysis:
                        system_prompt += f"\n\nAI Triage Information:\n- Practice Area: {ai_analysis.practice_area}\n- Category: {ai_analysis.category}\n- Complexity: {ai_analysis.complexity}\n- Identified Facts: {', '.join(ai_analysis.important_keywords)}"
                except LegalIssue.DoesNotExist:
                    pass
                    
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in history:
                if msg.get('role') in ['user', 'ai']:
                    role = 'assistant' if msg.get('role') == 'ai' else 'user'
                    messages.append({"role": role, "content": msg.get('content')})
                    
            messages.append({"role": "user", "content": query})
            
            log = AIRequestLog.objects.create(
                user=request.user,
                endpoint='consultation_chat',
                model_name=getattr(settings, 'GROQ_MODEL', 'openai/gpt-oss-120b'),
                prompt=str(messages)
            )
            
            completion = client.chat.completions.create(
                model=log.model_name,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )
            
            reply = completion.choices[0].message.content
            
            log.response = reply
            log.status_code = 200
            log.is_success = True
            log.save()
            
            return JsonResponse({'reply': reply})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ConsultationRoomView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def get(self, request, request_id):
        from apps.communication.models import Conversation
        
        try:
            consultation = ConsultationRequest.objects.get(id=request_id)
        except ConsultationRequest.DoesNotExist:
            return redirect('public_site:home')
            
        # Ensure user is part of it
        if request.user != consultation.client and request.user != consultation.lawyer.user:
            return redirect('public_site:home')
            
        if consultation.status not in ['ACTIVE', 'ACCEPTED']:
            return redirect(reverse('intake:consultation_status', kwargs={'request_id': consultation.id}))
            
        # Get or create conversation between them
        conversation = Conversation.objects.filter(
            participants=consultation.client
        ).filter(participants=consultation.lawyer.user).first()
        
        if not conversation:
            conversation = Conversation.objects.create(title=f"Consultation #{consultation.id}")
            conversation.participants.add(consultation.client, consultation.lawyer.user)
            
        context = {
            'consultation': consultation,
            'conversation': conversation,
            'issue': consultation.issue
        }
        return render(request, 'intake/consultation_room.html', context)


# AI LEGAL INTAKE API VIEWS

import json
from django.http import JsonResponse
from apps.ai.services.clarification import AIClarificationService
from apps.cases.models.case import Case, CaseStatus, MatterSource

class AILegalIntakeClarifyAPIView(LoginRequiredMixin, View):
    login_url = '/auth/client/login/'
    
    def post(self, request):
        data = json.loads(request.body)
        description = data.get('description', '')
        urgency = data.get('urgency', 'ROUTINE')
        category = data.get('category', '')
        
        issue = LegalIssue.objects.create(
            user=request.user,
            description=description,
            urgency=urgency,
            category=category,
            status='DRAFT'
        )
        
        clarification_data = AIClarificationService.generate_questions(issue)
        
        return JsonResponse({
            'issue_id': str(issue.id),
            'understanding_summary': clarification_data.get('understanding_summary', ''),
            'questions': clarification_data.get('questions', [])
        })

class AILegalIntakeSaveClarificationAPIView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        issue_id = data.get('issue_id')
        answers = data.get('answers', {})
        
        issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        issue.clarification_data = answers
        issue.save()
        
        return JsonResponse({'status': 'success'})

class AILegalIntakeUploadAPIView(LoginRequiredMixin, View):
    def post(self, request):
        issue_id = request.POST.get('issue_id')
        issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        
        for f in request.FILES.getlist('files'):
            DocumentUpload.objects.create(
                issue=issue,
                file=f,
                document_type='Intake_Evidence'
            )
            
        return JsonResponse({'status': 'success'})

class AILegalIntakeAnalyzeAPIView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        issue_id = data.get('issue_id')
        issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        
        AITriageService.analyze_issue(issue)
        issue.refresh_from_db()
        
        ai = getattr(issue, 'ai_analysis', None)
        historical_cases = HistoricalContextService.get_similar_cases(issue, ai) if ai else []
        
        # Serialize historical cases
        hc_serialized = []
        for hc in historical_cases:
            hc_serialized.append({
                'id': hc.id,
                'legal_issue': hc.legal_issue,
                'similarity': getattr(hc, 'similarity', 85),
                'court': hc.court_name,
                'year': hc.year,
                'duration': hc.duration,
                'disposition': hc.disposition
            })
            
        from apps.intake.services.matching import LawyerMatchService
        matched_lawyers_raw = LawyerMatchService.get_matched_lawyers(issue, ai) if ai else []
        matched_lawyers = []
        for ml in matched_lawyers_raw:
            lawyer = ml['lawyer']
            profile = getattr(lawyer.user, 'profile', None)
            matched_lawyers.append({
                'id': lawyer.id,
                'name': f"{lawyer.user.first_name} {lawyer.user.last_name}".strip(),
                'practice_area': lawyer.practice_areas[0] if getattr(lawyer, 'practice_areas', None) else '',
                'experience': lawyer.years_of_experience,
                'region': profile.city if profile else '',
                'match_score': ml['score'],
                'reasons': ml['reasons']
            })
            
        return JsonResponse({
            'analysis': {
                'category': ai.category if ai else 'Unknown',
                'subcategory': ai.subcategory if ai else 'Unknown',
                'urgency': issue.urgency,
                'complexity': ai.complexity if ai else 'Routine',
                'complexity_reasoning': 'Based on initial assessment',
                'required_documents': ai.suggested_documents if ai else [],
                'preliminary_assessment': ai.preliminary_assessment if ai else '',
                'assessment_reasoning': ai.assessment_reasoning if ai else '',
                'missing_information': ai.missing_information if ai else [],
                'suggested_next_steps': ai.suggested_next_steps if ai else [],
            },
            'historical_cases': hc_serialized,
            'matched_lawyers': matched_lawyers
        })

class AILegalIntakeSaveCaseAPIView(LoginRequiredMixin, View):
    def post(self, request):
        data = json.loads(request.body)
        issue_id = data.get('issue_id')
        lawyer_id = data.get('lawyer_id')
        issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        
        from apps.accounts.models import ProfessionalProfile
        lawyer = ProfessionalProfile.objects.filter(id=lawyer_id).first() if lawyer_id else None
        
        ai = getattr(issue, 'ai_analysis', None)
        
        from django.db import transaction
        with transaction.atomic():
            # Idempotency: Check if Case already exists for this AI Analysis
            existing_case = Case.objects.filter(ai_analysis_id=ai.id).first() if ai else None
            if existing_case:
                return JsonResponse({
                    'status': 'success',
                    'redirect_url': reverse('cases_ui:detail', kwargs={'pk': existing_case.id})
                })
            
            new_case = Case.objects.create(
                title=f"AI Intake: {ai.category if ai else 'Legal Issue'} - {issue.city}",
                description=issue.description,
                client=request.user.profile,
                assigned_lawyer=lawyer,
                matter_category=ai.category if ai else '',
                practice_area=ai.practice_area if ai else '',
                sub_category=ai.subcategory if ai else '',
                complexity=ai.complexity if ai else '',
                status=CaseStatus.PENDING_ACCEPTANCE,
                matter_source=MatterSource.AI_INTAKE,
                ai_analysis_id=ai.id if ai else None,
                incident_date=issue.incident_date,
                location=issue.city
            )
            
            if lawyer:
                from apps.notifications.models import Notification
                Notification.objects.create(
                    user=lawyer.user,
                    title="New AI Legal Intake Case",
                    message=f"You have a new AI Legal Intake case from {(request.user.first_name + ' ' + request.user.last_name).strip()}.",
                    notification_type='LAWYER_ASSIGNMENT',
                    target_url=reverse('lawyer_portal:dashboard')
                )
        
        # Transfer documents to Case without duplicating files
        from apps.documents.models import Document, DocumentType, DocumentCategory, DocumentStatus, DocumentVisibility
        
        dt, _ = DocumentType.objects.get_or_create(name='Evidence')
        dc, _ = DocumentCategory.objects.get_or_create(name='Client Upload')
        ds, _ = DocumentStatus.objects.get_or_create(name='Uploaded')
        dv, _ = DocumentVisibility.objects.get_or_create(name='Client Only')
        
        for upload in issue.documents.all():
            doc = Document.objects.create(
                document_number=f"DOC-{new_case.id}-{upload.id}",
                case=new_case,
                uploaded_by=request.user,
                owner=request.user,
                document_type=dt,
                category=dc,
                status=ds,
                visibility=dv,
                original_file=upload.file.name, # Pointing to same path!
                file_size=upload.file.size if upload.file else 0,
            )
        
        issue.status = 'ANALYZED'
        issue.save()
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('cases_ui:detail', kwargs={'pk': new_case.id})
        })
