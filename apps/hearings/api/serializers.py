from rest_framework import serializers
from apps.hearings.models import Hearing, Adjournment
from apps.hearings.models.master import AdjournmentReason
from apps.cases.models.master import CourtRoom

class HearingSerializer(serializers.ModelSerializer):
    case_title = serializers.CharField(source='case.title', read_only=True)
    case_number = serializers.CharField(source='case.case_number', read_only=True)
    client_name = serializers.CharField(source='case.client.name', read_only=True, default='')
    lawyer_name = serializers.CharField(source='case.assigned_lawyer.name', read_only=True, default='')

    class Meta:
        model = Hearing
        fields = '__all__'

class CalendarEventSerializer(serializers.ModelSerializer):
    id = serializers.CharField()
    title = serializers.SerializerMethodField()
    start = serializers.DateTimeField(source='start_time')
    end = serializers.DateTimeField(source='end_time')
    className = serializers.SerializerMethodField()
    extendedProps = serializers.SerializerMethodField()

    class Meta:
        model = Hearing
        fields = ['id', 'title', 'start', 'end', 'className', 'extendedProps']

    def get_title(self, obj):
        return f"{obj.case.case_number} - {obj.get_hearing_type_display()}"
        
    def get_className(self, obj):
        status_map = {
            'SCHEDULED': 'bg-primary',
            'CONFIRMED': 'bg-info',
            'COMPLETED': 'bg-success',
            'ADJOURNED': 'bg-warning',
            'CANCELLED': 'bg-danger',
        }
        return status_map.get(obj.status, 'bg-secondary')

    def get_extendedProps(self, obj):
        return {
            'case_id': str(obj.case.id),
            'status': obj.get_status_display(),
            'mode': obj.get_mode_display(),
            'priority': obj.get_priority_display(),
            'court_room': obj.court_room.room_number if obj.court_room else '',
        }
