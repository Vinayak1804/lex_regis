from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.common.validators.core import validate_probability, validate_positive_integer

class ValidatorsTest(TestCase):
    def test_validate_probability(self):
        validate_probability(0.5) # Should not raise
        with self.assertRaises(ValidationError):
            validate_probability(1.5)

    def test_validate_positive_integer(self):
        validate_positive_integer(10) # Should not raise
        with self.assertRaises(ValidationError):
            validate_positive_integer(-5)
