from rest_framework import serializers
from apps.hearings.models import Hearing, Adjournment
from apps.hearings.models.master import HearingStatus
from apps.cases.models.master import CourtRoom, HearingType

class HearingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hearing
        fields = '__all__'

class ScheduleHearingSerializer(serializers.Serializer):
    case_id = serializers.UUIDField()
    hearing_type_id = serializers.UUIDField()
    court_room_id = serializers.UUIDField(required=False, allow_null=True)
    presiding_judge_id = serializers.UUIDField(required=False, allow_null=True)
    scheduled_date = serializers.DateField()
    scheduled_time = serializers.TimeField()
    estimated_duration_minutes = serializers.IntegerField(default=30)

class AdjournmentRequestSerializer(serializers.Serializer):
    reason_id = serializers.UUIDField()
    remarks = serializers.CharField(required=False, allow_blank=True)

class AdjournmentGrantSerializer(serializers.Serializer):
    new_scheduled_date = serializers.DateField()
    new_scheduled_time = serializers.TimeField()
    new_duration_minutes = serializers.IntegerField(default=30)
