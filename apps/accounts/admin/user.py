from django.contrib import admin
from apps.accounts.models import User, Profile, ProfessionalProfile, Organization

class BaseAdmin(admin.ModelAdmin):
    list_per_page = 25
    save_on_top = True

@admin.register(User)
class UserAdmin(BaseAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'user_code', 'login_count', 'failed_login_attempts')

@admin.register(Profile)
class ProfileAdmin(BaseAdmin):
    list_display = ('user', 'nationality', 'city')
    search_fields = ('user__email',)

@admin.register(ProfessionalProfile)
class ProfessionalProfileAdmin(BaseAdmin):
    list_display = ('user', 'bar_council_number', 'law_firm')
    search_fields = ('user__email', 'bar_council_number')

@admin.register(Organization)
class OrganizationAdmin(BaseAdmin):
    list_display = ('firm_name', 'registration_number')
    search_fields = ('firm_name',)
