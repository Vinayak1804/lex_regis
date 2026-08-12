import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.common.constants.system import REGEX_PHONE, REGEX_PIN

def validate_phone_number(value):
    if not re.match(REGEX_PHONE, value):
        raise ValidationError(_("Invalid phone number format."))

def validate_pin_code(value):
    if not re.match(REGEX_PIN, value):
        raise ValidationError(_("Invalid PIN code format."))

def validate_bar_council_number(value):
    if not value.isalnum():
        raise ValidationError(_("Bar Council number must be alphanumeric."))

def validate_password_strength(value):
    if len(value) < 12:
        raise ValidationError(_("Password must be at least 12 characters."))
    if not any(char.isdigit() for char in value):
        raise ValidationError(_("Password must contain at least one digit."))
    if not any(char.isupper() for char in value):
        raise ValidationError(_("Password must contain at least one uppercase letter."))

def validate_probability(value):
    if not (0.0 <= value <= 1.0):
        raise ValidationError(_("Probability must be between 0 and 1."))

def validate_positive_integer(value):
    if value < 0:
        raise ValidationError(_("Value must be a positive integer."))
