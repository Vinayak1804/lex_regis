from django.contrib import admin
from apps.hearings.models import Hearing, Adjournment, JudgeSchedule
from apps.hearings.models.master import HearingStatus, AdjournmentReason

@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ('hearing_number', 'case', 'scheduled_date', 'scheduled_time', 'status', 'presiding_judge', 'court_room')
    list_filter = ('status', 'hearing_type', 'scheduled_date')
    search_fields = ('hearing_number', 'case__case_number')
    date_hierarchy = 'scheduled_date'
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
    
@admin.register(HearingStatus)
class HearingStatusAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'display_order')

@admin.register(AdjournmentReason)
class AdjournmentReasonAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'display_order')
