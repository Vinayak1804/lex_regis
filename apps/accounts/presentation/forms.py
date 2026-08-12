from django import forms
from apps.accounts.models import User, Profile, ProfessionalProfile, Organization, SecuritySettings, UserPreferences

class UserRegistrationStep1Form(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'preferred_language', 'timezone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_language': forms.Select(attrs={'class': 'form-select'}),
            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserRegistrationStep2Form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['role']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

class UserRegistrationStep3Form(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '000000', 'style': 'letter-spacing: 0.5em;'}))
    accept_terms = forms.BooleanField(required=True, label="I accept the Terms & Conditions and Privacy Policy", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'nationality', 'languages_known', 'short_bio', 
            'alternate_mobile', 'office_phone', 'address', 'city', 'state', 'country', 'pin_code',
            'emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone'
        ]
        widgets = {
            'short_bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})

class ProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ProfessionalProfile
        exclude = ['user', 'is_deleted', 'deleted_at', 'deleted_by', 'created_by', 'updated_by']
        widgets = {
            'office_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        exclude = ['user', 'is_deleted', 'deleted_at', 'deleted_by', 'created_by', 'updated_by']
        widgets = {
            'office_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})

class SecuritySettingsForm(forms.ModelForm):
    class Meta:
        model = SecuritySettings
        fields = ['two_factor_enabled', 'backup_email', 'backup_phone']
        widgets = {
            'two_factor_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'backup_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'backup_phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserPreferences
        exclude = ['user', 'is_deleted', 'deleted_at', 'deleted_by', 'created_by', 'updated_by']
        widgets = {
            'dark_mode': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ai_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ai_save_history': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ai_suggestions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'blockchain_verification_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput) and not isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({'class': 'form-control'})
