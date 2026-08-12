import uuid
import hashlib
import os
from django.utils import timezone

def generate_case_number(sequence: int) -> str:
    """Format: LR-YYYY-000001"""
    year = timezone.now().year
    seq_str = str(sequence).zfill(6)
    return f"LR-{year}-{seq_str}"

def generate_secure_file_name(original_name: str) -> str:
    ext = os.path.splitext(original_name)[1]
    return f"{uuid.uuid4().hex}{ext}"

def generate_uuid() -> str:
    return str(uuid.uuid4())
