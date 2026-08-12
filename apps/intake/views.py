from django.views.generic import TemplateView, View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.contrib import messages
from .models import LegalIssue, DocumentUpload, AIAnalysis, Recommendation

class IntakeLandingView(LoginRequiredMixin, TemplateView):
    template_name = 'intake/landing.html'

class IntakeWizardView(LoginRequiredMixin, View):
    def get(self, request):
        issue_id = request.GET.get('issue_id')
        context = {}
        if issue_id:
            try:
                context['issue'] = LegalIssue.objects.get(id=issue_id, user=request.user)
            except LegalIssue.DoesNotExist:
                pass
        return render(request, 'intake/wizard.html', context)
    
    def post(self, request):
        # Handle the form submission from the intake wizard
        # For now, just create a dummy issue and analysis, then redirect
        
        description = request.POST.get('description', '')
        incident_date = request.POST.get('incident_date') or None
        state = request.POST.get('state', '')
        district = request.POST.get('district', '')
        urgency = request.POST.get('urgency', 'ROUTINE')
        
        issue = LegalIssue.objects.create(
            user=request.user,
            description=description,
            incident_date=incident_date,
            state=state,
            district=district,
            urgency=urgency,
            status='ANALYZED'
        )
        
        # Handle files
        files = request.FILES.getlist('documents')
        for f in files:
            DocumentUpload.objects.create(issue=issue, file=f)
            
        import json
        from django.conf import settings
        from groq import Groq
        import logging
        import time
        import traceback
        from apps.ai.models import AIRequestLog
        
        logger = logging.getLogger('apps')
        start_time = time.time()
        
        log = AIRequestLog(
            user=request.user,
            endpoint='intake.analysis',
            model_name=settings.GROQ_MODEL if hasattr(settings, 'GROQ_MODEL') else 'llama-3.1-8b-instant',
        )
        
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = """You are an expert Indian Legal AI. Analyze the given legal issue and output a valid JSON object matching this exact structure, with no markdown or extra text:
{
    "category": "Broad category (e.g., Civil, Criminal, Corporate, Family)",
    "practice_area": "Specific practice area (e.g., Property Law, Divorce)",
    "subcategory": "Specific issue (e.g., Breach of Contract, Tenant Eviction)",
    "complexity": "Low, Medium, or High",
    "recommended_lawyer_type": "e.g., Civil Litigator, Corporate Counsel",
    "recommended_court": "e.g., District Court, High Court",
    "suggested_documents": ["List", "of", "documents"],
    "possible_acts": ["List", "of", "applicable", "acts"],
    "possible_sections": ["Specific sections"],
    "important_keywords": ["Keywords"],
    "suggested_next_steps": ["Step 1", "Step 2"],
    "timeline_estimate": "e.g., 6-12 Months",
    "cost_estimate": "e.g., ₹50,000-₹1,00,000",
    "risk_level": 50,
    "confidence_score": 85
}"""
            
            user_prompt = f"Issue Description: {description}\nIncident Date: {incident_date}\nState: {state}\nDistrict: {district}\nUrgency: {urgency}"
            log.prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            
            logger.info("Sending Groq request for AI Intake Analysis...")
            
            completion = client.chat.completions.create(
                model=log.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            latency = time.time() - start_time
            logger.info(f"Groq intake analysis completed in {latency:.2f}s")
            
            response_content = completion.choices[0].message.content
            
            # Log metrics
            log.response = response_content
            log.status_code = 200
            log.is_success = True
            log.latency_ms = latency * 1000
            if hasattr(completion, 'usage') and completion.usage:
                log.prompt_tokens = completion.usage.prompt_tokens
                log.completion_tokens = completion.usage.completion_tokens
                log.total_tokens = completion.usage.total_tokens
            log.save()
            
            try:
                ai_data = json.loads(response_content)
            except json.JSONDecodeError as je:
                logger.error(f"Failed to parse Groq JSON response: {response_content}")
                raise Exception("AI returned invalid data format.") from je
            
            AIAnalysis.objects.create(
                issue=issue,
                category=ai_data.get('category', 'General'),
                practice_area=ai_data.get('practice_area', 'General Practice'),
                subcategory=ai_data.get('subcategory', 'Legal Matter'),
                complexity=ai_data.get('complexity', 'Medium'),
                recommended_lawyer_type=ai_data.get('recommended_lawyer_type', 'Advocate'),
                recommended_court=ai_data.get('recommended_court', 'Appropriate Forum'),
                suggested_documents=ai_data.get('suggested_documents', []),
                possible_acts=ai_data.get('possible_acts', []),
                possible_sections=ai_data.get('possible_sections', []),
                important_keywords=ai_data.get('important_keywords', []),
                suggested_next_steps=ai_data.get('suggested_next_steps', []),
                timeline_estimate=ai_data.get('timeline_estimate', 'Unknown'),
                cost_estimate=ai_data.get('cost_estimate', 'To be determined'),
                risk_level=int(ai_data.get('risk_level', 50)),
                confidence_score=int(ai_data.get('confidence_score', 85))
            )
            
            messages.success(request, "Your issue has been dynamically analyzed by our AI.")
            return redirect(reverse('intake:wizard') + f'?issue_id={issue.id}')
            
        except Exception as e:
            logger.error(f"Groq API Error in Intake: {str(e)}\n{traceback.format_exc()}")
            log.status_code = getattr(e, 'status_code', 500)
            log.is_success = False
            log.latency_ms = (time.time() - start_time) * 1000
            log.error_message = str(e)
            log.traceback = traceback.format_exc()
            log.save()
            
            print("="*80)
            print("FULL AI ERROR")
            print(type(e))
            print(str(e))
            traceback.print_exc()
            print("="*80)
            raise

class LawyerRecommendationView(LoginRequiredMixin, View):
    def get(self, request, issue_id):
        issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        from apps.accounts.models import ProfessionalProfile
        import json
        from django.conf import settings
        from groq import Groq
        import logging
        import time
        import traceback
        from apps.ai.models import AIRequestLog
        
        logger = logging.getLogger('apps')
        start_time = time.time()
        
        log = AIRequestLog(
            user=request.user,
            endpoint='intake.lawyer_match',
            model_name=settings.GROQ_MODEL if hasattr(settings, 'GROQ_MODEL') else 'llama-3.1-8b-instant',
        )
        
        all_lawyers = list(ProfessionalProfile.objects.all()[:30]) # Limit to 30 for token constraints
        lawyers_data = []
        for lw in all_lawyers:
            lawyers_data.append({
                "id": str(lw.id),
                "name": f"{lw.user.first_name} {lw.user.last_name}",
                "practice_areas": lw.practice_areas,
                "experience": lw.years_of_experience
            })
            
        ai = getattr(issue, 'ai_analysis', None)
        issue_context = f"Description: {issue.description}\nPractice Area Needed: {ai.practice_area if ai else 'Unknown'}\nComplexity: {ai.complexity if ai else 'Unknown'}"
        
        try:
            client = Groq(api_key=settings.GROQ_API_KEY)
            
            system_prompt = """You are an expert Legal Matchmaker AI. Given a legal issue and a list of lawyers, return a JSON array of the top 3 recommended lawyer IDs based on their relevance to the issue. Output ONLY valid JSON matching this structure:
{
    "recommended_lawyer_ids": ["id1", "id2", "id3"]
}"""
            
            user_prompt = f"Issue:\n{issue_context}\n\nLawyers:\n{json.dumps(lawyers_data)}"
            
            log.prompt = f"System: {system_prompt}\n\nUser: {user_prompt}"
            logger.info(f"Sending Groq request for Lawyer Recommendation... (Evaluating {len(all_lawyers)} lawyers)")
            
            completion = client.chat.completions.create(
                model=log.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            latency = time.time() - start_time
            logger.info(f"Groq lawyer recommendation completed in {latency:.2f}s")
            
            response_content = completion.choices[0].message.content
            
            # Log metrics
            log.response = response_content
            log.status_code = 200
            log.is_success = True
            log.latency_ms = latency * 1000
            if hasattr(completion, 'usage') and completion.usage:
                log.prompt_tokens = completion.usage.prompt_tokens
                log.completion_tokens = completion.usage.completion_tokens
                log.total_tokens = completion.usage.total_tokens
            log.save()
            
            ai_data = json.loads(response_content)
            recommended_ids = ai_data.get('recommended_lawyer_ids', [])
            
            lawyers = []
            for rid in recommended_ids:
                lw = next((l for l in all_lawyers if str(l.id) == str(rid)), None)
                if lw:
                    lawyers.append(lw)
                    
            if not lawyers:
                lawyers = all_lawyers[:5]
                
        except Exception as e:
            logger.error(f"Groq API Error in Recommendation: {str(e)}\n{traceback.format_exc()}")
            log.status_code = getattr(e, 'status_code', 500)
            log.is_success = False
            log.latency_ms = (time.time() - start_time) * 1000
            log.error_message = str(e)
            log.traceback = traceback.format_exc()
            log.save()
            
            print("="*80)
            print("FULL AI ERROR")
            print(type(e))
            print(str(e))
            traceback.print_exc()
            print("="*80)
            raise
            
        context = {
            'issue': issue,
            'lawyers': lawyers
        }
        return render(request, 'intake/recommendations.html', context)

class BookLawyerView(LoginRequiredMixin, View):
    def post(self, request, issue_id):
        issue = LegalIssue.objects.get(id=issue_id, user=request.user)
        lawyer_id = request.POST.get('lawyer_id')
        from apps.accounts.models import ProfessionalProfile
        lawyer = ProfessionalProfile.objects.get(id=lawyer_id)
        
        from .models import ConsultationRequest
        from apps.cases.models.case import Case, CaseStatus, MatterSource
        
        # Grab snapshot data
        ai = getattr(issue, 'ai_analysis', None)
        
        ConsultationRequest.objects.create(
            client=request.user,
            lawyer=lawyer,
            issue=issue,
            status='PENDING',
            matter_category=ai.category if ai else '',
            practice_area=ai.practice_area if ai else '',
            estimated_budget=ai.cost_estimate if ai else '',
            timeline=ai.timeline_estimate if ai else ''
        )
        
        # Create persistent Case object from AI Intake
        new_case = Case.objects.create(
            title=f"{ai.subcategory if ai else 'Legal Matter'} - {issue.district}",
            description=issue.description,
            ai_summary=", ".join(ai.important_keywords) if ai and ai.important_keywords else '',
            client=request.user.profile,
            assigned_lawyer=lawyer,
            matter_category=ai.category if ai else '',
            practice_area=ai.practice_area if ai else '',
            sub_category=ai.subcategory if ai else '',
            complexity=ai.complexity if ai else '',
            risk_level=str(ai.risk_level) if ai else '',
            timeline_estimate=ai.timeline_estimate if ai else '',
            priority=issue.urgency,
            court=ai.recommended_court if ai else '',
            location=f"{issue.district}, {issue.state}" if issue.district else issue.state,
            status=CaseStatus.PENDING_ACCEPTANCE,
            matter_source=MatterSource.AI_INTAKE,
            ai_confidence=ai.confidence_score if ai else None,
            incident_date=issue.incident_date,
            ai_analysis_id=ai.id if ai else None
        )
        
        issue.status = 'LAWYER_BOOKED'
        issue.save()
        
        from apps.communication.models import Conversation, Message
        from apps.notifications.models import Notification

        # Create Conversation
        conv = Conversation.objects.create(case=new_case)
        conv.participants.add(request.user, lawyer.user)
        
        # Initial Message
        Message.objects.create(
            conversation=conv,
            sender=request.user,
            content=f"Consultation requested for issue: {issue.description[:100]}..."
        )

        # Create Notification
        Notification.objects.create(
            user=lawyer.user,
            title="New Case Request",
            message=f"You have a new consultation request for a {ai.practice_area if ai else 'legal matter'}.",
            notification_type='LAWYER_ASSIGNMENT',
            target_url=reverse('lawyer_portal:dashboard')
        )
        
        messages.success(request, f"Consultation requested and Case {new_case.case_number} has been created!")
        return redirect('dashboard:index')
