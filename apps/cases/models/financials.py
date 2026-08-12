from django.db import models
from apps.common.models.base import BaseModel
from .case import Case

class CaseFinancial(BaseModel):
    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='financials')
    
    professional_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    court_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    government_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    travel_expenses = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    miscellaneous = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    gst_amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    
    invoice_number = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=50, default='UNPAID')
    
    @property
    def total_amount(self):
        return (
            self.professional_fee +
            self.court_fee +
            self.government_fee +
            self.travel_expenses +
            self.miscellaneous +
            self.gst_amount
        )

    def __str__(self):
        return f"Financials for {self.case.case_number}"
