import os
import uuid
from django.utils import timezone

def get_profile_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('profile_images', timezone.now().strftime('%Y/%m/%d'), filename)

def get_document_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', timezone.now().strftime('%Y/%m/%d'), filename)

def get_organization_logo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('organization_logos', timezone.now().strftime('%Y/%m/%d'), filename)
