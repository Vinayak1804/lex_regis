import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_aadhaar(value):
    if not re.match(r'^\d{12}$', value):
        raise ValidationError(_("Invalid Aadhaar format. Must be 12 digits."))

def validate_pan(value):
    if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', value):
        raise ValidationError(_("Invalid PAN format."))

def validate_bar_council_number(value):
    if not re.match(r'^[A-Z]{2}/\d{1,5}/\d{4}$', value):
        raise ValidationError(_("Invalid Bar Council Registration Number format. Expected: XX/12345/YYYY"))

def validate_case_number(value):
    if not re.match(r'^LR-\d{4}-\d{6}$', value):
        raise ValidationError(_("Invalid Case Number format. Expected: LR-YYYY-XXXXXX"))
