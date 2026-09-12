from django import forms
from apps.hearings.models import Hearing

class HearingScheduleForm(forms.ModelForm):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    
    class Meta:
        model = Hearing
        fields = [
            'case', 'title', 'hearing_type', 'mode', 'priority',
            'start_time', 'end_time', 'court_room', 'presiding_judge',
            'notes'
        ]
        widgets = {
            'case': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'hearing_type': forms.Select(attrs={'class': 'form-select'}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'court_room': forms.Select(attrs={'class': 'form-select'}),
            'presiding_judge': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError("End time must be after start time.")
            
        return cleaned_data
