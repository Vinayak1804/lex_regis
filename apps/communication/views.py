from django.views.generic import CreateView, ListView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden

from .models import (
    LawyerRequest, LawyerRequestStatus, Conversation,
    ConversationStatus, Message, MessageStatus
)
from apps.accounts.models import ProfessionalProfile
from apps.cases.models import Case, CaseStatus
from django.utils import timezone

class RequestConsultationView(LoginRequiredMixin, CreateView):
    model = LawyerRequest
    fields = ['case', 'initial_message']
    template_name = 'communication/request_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lawyer'] = get_object_or_404(ProfessionalProfile, pk=self.kwargs['lawyer_id'])
        # Optional: restrict case selection to client's cases
        context['client_cases'] = Case.objects.filter(client=self.request.user.profile)
        return context

    def form_valid(self, form):
        lawyer = get_object_or_404(ProfessionalProfile, pk=self.kwargs['lawyer_id'])
        form.instance.client = self.request.user.profile
        form.instance.lawyer = lawyer
        form.instance.status = LawyerRequestStatus.PENDING
        messages.success(self.request, f"Consultation requested with {lawyer.user.get_full_name()}.")
        return super().form_valid(form)
        
    def get_success_url(self):
        return reverse('dashboard:home') # redirect to client dashboard

class IncomingRequestsView(LoginRequiredMixin, ListView):
    model = LawyerRequest
    template_name = 'communication/incoming_requests.html'
    context_object_name = 'requests'
    
    def get_queryset(self):
        if not hasattr(self.request.user, 'professional_profile'):
            return LawyerRequest.objects.none()
        return LawyerRequest.objects.filter(
            lawyer=self.request.user.professional_profile,
            status=LawyerRequestStatus.PENDING
        ).order_by('-requested_at')

class AcceptRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        req = get_object_or_404(LawyerRequest, pk=pk)
        
        # Verify lawyer
        if req.lawyer.user != request.user:
            return HttpResponseForbidden("You do not have permission to accept this request.")
            
        with transaction.atomic():
            req.status = LawyerRequestStatus.ACCEPTED
            req.accepted_at = timezone.now()
            req.save()
            
            # Use existing case if provided, or create one (Simplified for now, assuming case is linked or none)
            case = req.case
            if case:
                case.assigned_lawyer = req.lawyer
                if case.status == CaseStatus.DRAFT or case.status == CaseStatus.PENDING_ACCEPTANCE:
                    case.status = CaseStatus.LAWYER_ASSIGNED
                case.save()
            else:
                # If business logic demands, create a case here. For demo, we just use the conversation.
                pass
                
            # Find or create conversation
            conv, created = Conversation.objects.get_or_create(
                case=case,
                defaults={'status': ConversationStatus.ACTIVE}
            )
            
            if not created:
                conv.status = ConversationStatus.ACTIVE
                conv.save()
            
            conv.participants.add(req.client.user)
            conv.participants.add(req.lawyer.user)
            
            # System Message
            Message.objects.create(
                conversation=conv,
                sender=req.lawyer.user,
                content=f"Consultation request accepted. You can now communicate securely regarding your case.",
                status=MessageStatus.SENT
            )
            
            # TODO: Create Notification (if notifications app is available)
            
        messages.success(request, "Request accepted. Conversation is now active.")
        return redirect('communication:messages')

class DeclineRequestView(LoginRequiredMixin, View):
    def post(self, request, pk):
        req = get_object_or_404(LawyerRequest, pk=pk)
        
        if req.lawyer.user != request.user:
            return HttpResponseForbidden("You do not have permission to decline this request.")
            
        req.status = LawyerRequestStatus.DECLINED
        req.declined_at = timezone.now()
        req.save()
        
        messages.info(request, "Request declined.")
        return redirect('communication:incoming_requests')

class MessagesView(LoginRequiredMixin, TemplateView):
    template_name = 'communication/messages.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load active conversations for the user
        context['conversations'] = self.request.user.conversations.filter(
            status__in=[ConversationStatus.ACTIVE, ConversationStatus.CLOSED]
        ).order_by('-last_message_at', '-updated_at')
        return context

class ConversationDetailAPIView(LoginRequiredMixin, View):
    def get(self, request, pk):
        from django.http import JsonResponse
        conv = get_object_or_404(Conversation, pk=pk)
        
        if request.user not in conv.participants.all():
            return HttpResponseForbidden("Not a participant")
            
        messages = conv.messages.all().order_by('created_at')[:50] # Pagination can be added here
        data = [{
            'id': m.id,
            'sender_id': m.sender.id,
            'sender_name': m.sender.get_full_name(),
            'content': m.content,
            'created_at': m.created_at.isoformat(),
            'is_read': m.is_read,
            'status': m.status
        } for m in messages]
        
        return JsonResponse({'messages': data})
