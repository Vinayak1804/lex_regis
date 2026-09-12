from django.contrib import admin
from apps.hearings.models import Hearing, Adjournment, JudgeSchedule
from apps.hearings.models.master import AdjournmentReason

@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ('hearing_number', 'case', 'start_time', 'end_time', 'status', 'presiding_judge', 'court_room')
    list_filter = ('status', 'hearing_type', 'start_time')
    search_fields = ('hearing_number', 'case__case_number')
    date_hierarchy = 'start_time'
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

@admin.register(Adjournment)
class AdjournmentAdmin(admin.ModelAdmin):
    list_display = ('hearing', 'reason', 'requested_by', 'granted', 'new_scheduled_date')
    list_filter = ('granted', 'reason')
    search_fields = ('hearing__hearing_number',)
    readonly_fields = ('created_at', 'updated_at', 'deleted_at')

@admin.register(JudgeSchedule)
class JudgeScheduleAdmin(admin.ModelAdmin):
    list_display = ('judge', 'date', 'is_available', 'start_time', 'end_time')
    list_filter = ('is_available', 'date')
    search_fields = ('judge__username', 'judge__email')
    date_hierarchy = 'date'
    
@admin.register(AdjournmentReason)
class AdjournmentReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'display_order')
