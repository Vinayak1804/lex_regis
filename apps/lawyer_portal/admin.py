from django.contrib import admin
from .models import (
    LawyerProfile, LawyerEducation, LawyerPracticeArea,
    LawyerOffice, LawyerFees, LawyerAvailability, LawyerVerification
)

admin.site.register(LawyerProfile)
admin.site.register(LawyerEducation)
admin.site.register(LawyerPracticeArea)
admin.site.register(LawyerOffice)
admin.site.register(LawyerFees)
admin.site.register(LawyerAvailability)
admin.site.register(LawyerVerification)
