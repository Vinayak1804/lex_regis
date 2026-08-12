from django import forms
from apps.hearings.models import Hearing
from django.utils import timezone

class HearingScheduleForm(forms.ModelForm):
    scheduled_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    scheduled_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    
    class Meta:
        model = Hearing
        fields = ['case', 'scheduled_date', 'scheduled_time', 'estimated_duration_minutes', 'hearing_type', 'court_room', 'presiding_judge']
        widgets = {
            'case': forms.Select(attrs={'class': 'form-select'}),
            'estimated_duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'hearing_type': forms.Select(attrs={'class': 'form-select'}),
            'court_room': forms.Select(attrs={'class': 'form-select'}),
            'presiding_judge': forms.Select(attrs={'class': 'form-select'}),
        }
