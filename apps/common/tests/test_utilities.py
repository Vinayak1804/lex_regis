from django.test import TestCase
from apps.common.utilities.generators import generate_uuid, generate_sha256

class UtilitiesTest(TestCase):
    def test_generate_uuid(self):
        val = generate_uuid()
        self.assertTrue(isinstance(val, str))

    def test_generate_sha256(self):
        val = generate_sha256("test")
        self.assertEqual(len(val), 64)
