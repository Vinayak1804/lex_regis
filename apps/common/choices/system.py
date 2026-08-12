from django.db import models

class RoleChoices(models.TextChoices):
    ADMIN = 'ADMIN', 'Administrator'
    ADVOCATE = 'ADVOCATE', 'Advocate'
    LAW_FIRM = 'LAW_FIRM', 'Law Firm'
    CLIENT = 'CLIENT', 'Client / Citizen'

class GenderChoices(models.TextChoices):
    MALE = 'MALE', 'Male'
    FEMALE = 'FEMALE', 'Female'
    OTHER = 'OTHER', 'Other'

class PriorityChoices(models.TextChoices):
    LOW = 'LOW', 'Low'
    MEDIUM = 'MEDIUM', 'Medium'
    HIGH = 'HIGH', 'High'
    CRITICAL = 'CRITICAL', 'Critical'

class VisibilityChoices(models.TextChoices):
    PUBLIC = 'PUBLIC', 'Public'
    PRIVATE = 'PRIVATE', 'Private'
    RESTRICTED = 'RESTRICTED', 'Restricted'

class CaseStatusChoices(models.TextChoices):
    OPEN = 'OPEN', 'Open'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    CLOSED = 'CLOSED', 'Closed'
    ARCHIVED = 'ARCHIVED', 'Archived'

class NotificationTypeChoices(models.TextChoices):
    EMAIL = 'EMAIL', 'Email'
    SMS = 'SMS', 'SMS'
    PUSH = 'PUSH', 'Push'
    IN_APP = 'IN_APP', 'In-App'

class IdentityTypeChoices(models.TextChoices):
    PASSPORT = 'PASSPORT', 'Passport'
    NATIONAL_ID = 'NATIONAL_ID', 'National ID'
    DRIVERS_LICENSE = 'DRIVERS_LICENSE', 'Driver\'s License'

class VerificationStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'

class LanguageChoices(models.TextChoices):
    EN = 'EN', 'English'
    ES = 'ES', 'Spanish'
    FR = 'FR', 'French'

class PaymentStatusChoices(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    COMPLETED = 'COMPLETED', 'Completed'
    FAILED = 'FAILED', 'Failed'
    REFUNDED = 'REFUNDED', 'Refunded'

class DocumentStatusChoices(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    UPLOADED = 'UPLOADED', 'Uploaded'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'

class DocumentFileTypeChoices(models.TextChoices):
    PDF = 'PDF', 'PDF Document'
    DOCX = 'DOCX', 'Word Document'
    JPG = 'JPG', 'JPEG Image'
    PNG = 'PNG', 'PNG Image'
    TXT = 'TXT', 'Text File'
    CSV = 'CSV', 'CSV File'

class MimeTypeChoices(models.TextChoices):
    APPLICATION_PDF = 'application/pdf', 'PDF'
    APPLICATION_DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'DOCX'
    IMAGE_JPEG = 'image/jpeg', 'JPEG'
    IMAGE_PNG = 'image/png', 'PNG'
    TEXT_PLAIN = 'text/plain', 'TXT'
    TEXT_CSV = 'text/csv', 'CSV'
