from django.contrib import admin
from .models import LegalIssue, DocumentUpload, AIAnalysis, Recommendation, SearchHistory, ConsultationRequest

admin.site.register(LegalIssue)
admin.site.register(DocumentUpload)
admin.site.register(AIAnalysis)
admin.site.register(Recommendation)
admin.site.register(SearchHistory)

@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'lawyer', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('client__email', 'client__first_name', 'lawyer__user__email')
