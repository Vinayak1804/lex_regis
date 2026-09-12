from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..selectors import AIChatSelector
from ..services import AIChatService
from apps.cases.models import Case
from apps.documents.models import Document

class AIChatView(LoginRequiredMixin, TemplateView):
    template_name = 'ai/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get query params for specific context
        case_id = self.request.GET.get('case_id')
        doc_id = self.request.GET.get('doc_id')
        
        case = None
        document = None
        
        if case_id:
            case = Case.objects.filter(id=case_id).first()
        if doc_id:
            document = Document.objects.filter(id=doc_id).first()
            
        # Get or create conversation for this context
        conversation = AIChatService.get_or_create_conversation(self.request.user, case, document)
        
        context['conversation'] = conversation
        context['messages'] = AIChatSelector.get_conversation_messages(conversation)
        context['recent_conversations'] = AIChatSelector.get_user_conversations(self.request.user)[:10]
        
        return context

class AIChatMessageCreateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        conv_id = request.POST.get('conversation_id')
        content = request.POST.get('content')
        
        if not conv_id or not content:
            return HttpResponse("Invalid request", status=400)
            
        conversation = AIChatSelector.get_conversation(conv_id, request.user)
        if not conversation:
            return HttpResponse("Conversation not found", status=404)
            
        # Process message via AI service
        messages = AIChatService.process_user_message(conversation, content)
        
        # We can return just the new messages as an HTMX fragment
        return render(request, 'ai/partials/message_list.html', {
            'messages': AIChatSelector.get_conversation_messages(conversation)
        })

class AIDiagnosticsView(LoginRequiredMixin, View):
    def get(self, request):
        from django.conf import settings
        from groq import Groq
        import time
        from django.db.models import Avg, Count, Sum, Max, Min
        from django.utils import timezone
        import datetime
        from apps.ai.models import AIRequestLog
        import psutil
        import sys
        import django
        
        # Ensure only staff/admins can view this
        if not request.user.is_staff:
            return HttpResponse("Unauthorized", status=401)
            
        status = "Unknown"
        latency = "N/A"
        error_msg = None
        model_name = getattr(settings, 'GROQ_MODEL', "openai/gpt-oss-120b")
        
        try:
            start = time.time()
            client = Groq(api_key=settings.GROQ_API_KEY)
            client.models.list()
            latency = f"{(time.time() - start) * 1000:.0f} ms"
            status = "Connected"
        except Exception as e:
            status = "Disconnected"
            error_msg = str(e)
            
        today = timezone.now().date()
        today_logs = AIRequestLog.objects.filter(created_at__date=today)
        
        requests_today = today_logs.count()
        successful_requests = today_logs.filter(is_success=True).count()
        failed_requests = today_logs.filter(is_success=False).count()
        
        avg_latency = today_logs.filter(is_success=True).aggregate(Avg('latency_ms'))['latency_ms__avg']
        avg_latency = f"{avg_latency:.0f} ms" if avg_latency else "N/A"
        
        fastest = today_logs.filter(is_success=True).aggregate(Min('latency_ms'))['latency_ms__min']
        fastest = f"{fastest:.0f} ms" if fastest else "N/A"
        
        slowest = today_logs.filter(is_success=True).aggregate(Max('latency_ms'))['latency_ms__max']
        slowest = f"{slowest:.0f} ms" if slowest else "N/A"
        
        total_tokens = today_logs.aggregate(Sum('total_tokens'))['total_tokens__sum'] or 0
        prompt_tokens = today_logs.aggregate(Sum('prompt_tokens'))['prompt_tokens__sum'] or 0
        completion_tokens = today_logs.aggregate(Sum('completion_tokens'))['completion_tokens__sum'] or 0
        
        avg_tokens = total_tokens / requests_today if requests_today > 0 else 0
        
        # Estimated cost calculation: Llama 3.1 8b is approx $0.05 per 1M input and $0.08 per 1M output tokens
        estimated_cost = (prompt_tokens / 1_000_000 * 0.05) + (completion_tokens / 1_000_000 * 0.08)
        
        recent_requests = AIRequestLog.objects.all()[:15]
        failed_requests_list = AIRequestLog.objects.filter(is_success=False)[:10]
            
        context = {
            'status': status,
            'api_key_loaded': bool(settings.GROQ_API_KEY),
            'model': model_name,
            'latency': latency,
            'error': error_msg,
            
            # System Status
            'django_version': django.get_version(),
            'python_version': sys.version.split(' ')[0],
            'server_cpu': psutil.cpu_percent(),
            'server_ram': psutil.virtual_memory().percent,
            
            # Live Metrics
            'requests_today': requests_today,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'avg_latency': avg_latency,
            'fastest_response': fastest,
            'slowest_response': slowest,
            'avg_tokens': f"{avg_tokens:.0f}",
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'estimated_cost': f"${estimated_cost:.4f}",
            
            'recent_requests': recent_requests,
            'failed_requests_list': failed_requests_list,
        }
        return render(request, 'ai/diagnostics.html', context)
