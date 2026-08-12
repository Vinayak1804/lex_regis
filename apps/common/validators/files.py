import os
from django.core.exceptions import ValidationError

MAX_DOCUMENT_SIZE = 5 * 1024 * 1024 # 5 MB
MAX_IMAGE_SIZE = 2 * 1024 * 1024 # 2 MB
MAX_AUDIO_SIZE = 10 * 1024 * 1024 # 10 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024 # 50 MB

def validate_document_extension(value):
    valid_extensions = ['.pdf', '.doc', '.docx']
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported document extension.")

def validate_image_extension(value):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported image extension.")

def validate_audio_extension(value):
    valid_extensions = ['.mp3', '.wav']
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported audio extension.")

def validate_video_extension(value):
    valid_extensions = ['.mp4', '.avi']
    ext = os.path.splitext(value.name)[1]
    if not ext.lower() in valid_extensions:
        raise ValidationError("Unsupported video extension.")

def validate_document_size(value):
    if value.size > MAX_DOCUMENT_SIZE:
        raise ValidationError(f"Document size exceeds maximum limit of {MAX_DOCUMENT_SIZE/1024/1024} MB.")

def validate_image_size(value):
    if value.size > MAX_IMAGE_SIZE:
        raise ValidationError(f"Image size exceeds maximum limit of {MAX_IMAGE_SIZE/1024/1024} MB.")

def validate_audio_size(value):
    if value.size > MAX_AUDIO_SIZE:
        raise ValidationError(f"Audio size exceeds maximum limit of {MAX_AUDIO_SIZE/1024/1024} MB.")

def validate_video_size(value):
    if value.size > MAX_VIDEO_SIZE:
        raise ValidationError(f"Video size exceeds maximum limit of {MAX_VIDEO_SIZE/1024/1024} MB.")
