from django import forms
from .models import (
    LawyerProfile, LawyerEducation, LawyerOffice, 
    LawyerFees, LawyerAvailability, LawyerVerification,
    LawyerPracticeArea
)

class LawyerRegistrationStep1Form(forms.ModelForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    gender = forms.ChoiceField(choices=[('MALE', 'Male'), ('FEMALE', 'Female'), ('OTHER', 'Other')])
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    nationality = forms.CharField(max_length=50, initial='Indian')
    
    class Meta:
        model = LawyerProfile
        fields = ['biography', 'languages']

class LawyerRegistrationStep2Form(forms.ModelForm):
    class Meta:
        model = LawyerProfile
        fields = [
            'bar_council_number', 'enrollment_number', 'enrollment_date',
            'state_bar_council', 'supreme_court_reg', 'law_firm', 'designation',
            'years_of_experience', 'professional_email', 'professional_website', 'linkedin'
        ]
        widgets = {
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
        }

class LawyerRegistrationStep3Form(forms.ModelForm):
    class Meta:
        model = LawyerEducation
        exclude = ['lawyer']

class LawyerRegistrationStep4Form(forms.Form):
    practice_areas = forms.MultipleChoiceField(
        choices=[
            ('Civil', 'Civil'),
            ('Criminal', 'Criminal'),
            ('Corporate', 'Corporate'),
            ('Family', 'Family'),
            ('Tax', 'Tax'),
            ('Cyber', 'Cyber'),
            ('Property', 'Property'),
            ('Consumer', 'Consumer'),
            ('Employment', 'Employment'),
            ('Labour', 'Labour'),
            ('Insurance', 'Insurance'),
            ('IPR', 'IPR'),
            ('Banking', 'Banking'),
            ('Constitutional', 'Constitutional'),
            ('Environment', 'Environment'),
            ('Human Rights', 'Human Rights'),
            ('Immigration', 'Immigration'),
            ('Arbitration', 'Arbitration'),
            ('Company Law', 'Company Law'),
            ('Motor Accident', 'Motor Accident'),
            ('Cheque Bounce', 'Cheque Bounce'),
            ('Land Acquisition', 'Land Acquisition'),
        ],
        widget=forms.CheckboxSelectMultiple
    )

class LawyerRegistrationStep5Form(forms.Form):
    court_preferences = forms.MultipleChoiceField(
        choices=[
            ('Supreme Court', 'Supreme Court'),
            ('High Court', 'High Court'),
            ('District Court', 'District Court'),
            ('Family Court', 'Family Court'),
            ('Consumer Court', 'Consumer Court'),
            ('Tribunal', 'Tribunal'),
            ('Sessions Court', 'Sessions Court'),
            ('Special Court', 'Special Court'),
        ],
        widget=forms.CheckboxSelectMultiple
    )

class LawyerRegistrationStep6Form(forms.ModelForm):
    class Meta:
        model = LawyerOffice
        exclude = ['lawyer']

class LawyerRegistrationStep7Form(forms.ModelForm):
    class Meta:
        model = LawyerAvailability
        exclude = ['lawyer']

class LawyerRegistrationStep8Form(forms.ModelForm):
    class Meta:
        model = LawyerFees
        exclude = ['lawyer']

class LawyerRegistrationStep9Form(forms.ModelForm):
    class Meta:
        model = LawyerVerification
        fields = ['bar_council_cert', 'identity_proof', 'practice_cert', 'office_proof']
