from rest_framework import serializers
from apps.cases.models import Case, CaseTimeline

class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = '__all__'

class CaseTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseTimeline
        fields = '__all__'
