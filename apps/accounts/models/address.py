from django.db import models
from apps.common.models.base import BaseModel

class Address(BaseModel):
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    locality = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=20)
    landmark = models.CharField(max_length=200, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    def __str__(self):
        return f"{self.locality}, {self.city}, {self.state}"
