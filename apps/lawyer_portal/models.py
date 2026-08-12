from django.db import models
from django.conf import settings
from apps.common.models.base import BaseModel

class LawyerProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portal_profile')
    bar_council_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    enrollment_number = models.CharField(max_length=50, blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)
    state_bar_council = models.CharField(max_length=100, blank=True, null=True)
    supreme_court_reg = models.CharField(max_length=100, blank=True, null=True)
    
    law_firm = models.CharField(max_length=150, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    professional_email = models.EmailField(blank=True, null=True)
    professional_website = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    
    biography = models.TextField(blank=True, null=True)
    languages = models.JSONField(default=list, blank=True)
    
    # Aggregated Stats
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    cases_handled = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

class LawyerEducation(BaseModel):
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='education')
    llb_university = models.CharField(max_length=150, blank=True)
    llb_year = models.PositiveIntegerField(blank=True, null=True)
    llm_university = models.CharField(max_length=150, blank=True)
    llm_year = models.PositiveIntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=150, blank=True)
    phd_year = models.PositiveIntegerField(blank=True, null=True)
    
    certificates = models.JSONField(default=list, blank=True)
    specialisations = models.JSONField(default=list, blank=True)

class LawyerPracticeArea(BaseModel):
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='practice_areas')
    area_name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('lawyer', 'area_name')

class LawyerOffice(BaseModel):
    lawyer = models.ForeignKey(LawyerProfile, on_delete=models.CASCADE, related_name='offices')
    office_name = models.CharField(max_length=150)
    address = models.TextField()
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pin_code = models.CharField(max_length=20)
    google_maps_link = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

class LawyerFees(BaseModel):
    lawyer = models.OneToOneField(LawyerProfile, on_delete=models.CASCADE, related_name='fees')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    video_consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    office_visit_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    drafting_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    legal_notice_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    court_appearance_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    document_review_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    retainer_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    min_matter_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preferred_matter_size = models.CharField(max_length=50, blank=True)

class LawyerAvailability(BaseModel):
    lawyer = models.OneToOneField(LawyerProfile, on_delete=models.CASCADE, related_name='availability')
    online_consultation = models.BooleanField(default=True)
    office_consultation = models.BooleanField(default=True)
    video_consultation = models.BooleanField(default=True)
    phone_consultation = models.BooleanField(default=True)
    emergency_consultation = models.BooleanField(default=False)
    
    working_days = models.JSONField(default=list) # e.g. ["Mon", "Tue", "Wed", "Thu", "Fri"]
    working_hours = models.CharField(max_length=100, default="10:00 AM - 6:00 PM")

class LawyerVerification(BaseModel):
    lawyer = models.OneToOneField(LawyerProfile, on_delete=models.CASCADE, related_name='verification')
    bar_council_cert = models.FileField(upload_to='lawyer_docs/bar_council/', blank=True)
    identity_proof = models.FileField(upload_to='lawyer_docs/identity/', blank=True)
    practice_cert = models.FileField(upload_to='lawyer_docs/practice/', blank=True)
    office_proof = models.FileField(upload_to='lawyer_docs/office/', blank=True)
    
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
