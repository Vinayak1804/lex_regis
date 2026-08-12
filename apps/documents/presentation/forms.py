from django import forms
from apps.documents.models import Document

class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Document
        fields = ['case', 'document_type', 'category', 'status', 'visibility', 'description']
        widgets = {
            'case': forms.Select(attrs={'class': 'form-select'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
