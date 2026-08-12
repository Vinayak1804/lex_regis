from apps.common.utilities.paths import get_profile_image_path
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from apps.common.models.base import BaseModel
from apps.common.choices.system import RoleChoices, GenderChoices, LanguageChoices
from apps.common.validators.core import validate_phone_number

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', RoleChoices.ADMIN)
        return self.create_user(email, password, **extra_fields)

class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, validators=[validate_phone_number], blank=True, null=True)
    
    role = models.CharField(max_length=20, choices=RoleChoices.choices)
    gender = models.CharField(max_length=20, choices=GenderChoices.choices, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_photo = models.ImageField(upload_to=get_profile_image_path, blank=True, null=True)
    
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    two_factor_enabled = models.BooleanField(default=False)
    
    preferred_language = models.CharField(max_length=10, choices=LanguageChoices.choices, default=LanguageChoices.EN)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # System Information
    user_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    account_status = models.CharField(max_length=20, default='ACTIVE')
    login_count = models.PositiveIntegerField(default=0)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    def __str__(self):
        return self.email
