from django.contrib import admin
from apps.cases.models.case import Case

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'title', 'client', 'assigned_lawyer', 'status', 'priority', 'created_at')
    list_filter = ('status', 'priority', 'matter_source', 'matter_category')
    search_fields = ('case_number', 'title', 'description', 'client__user__email', 'assigned_lawyer__user__email')
    readonly_fields = ('case_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('case_number', 'title', 'description', 'ai_summary', 'matter_source', 'ai_analysis_id', 'status', 'priority')
        }),
        ('Parties', {
            'fields': ('client', 'assigned_lawyer', 'assigned_law_firm', 'opponent_name')
        }),
        ('Classification', {
            'fields': ('matter_category', 'practice_area', 'sub_category', 'complexity', 'risk_level')
        }),
        ('Estimates', {
            'fields': ('timeline_estimate', 'budget_estimate', 'case_value')
        }),
        ('Location Details', {
            'fields': ('court', 'location', 'incident_date')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
