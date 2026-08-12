from django.contrib import admin

class SearchMixin:
    search_fields = ('id',)

class FilterMixin:
    list_filter = ('created_at', 'is_active', 'is_deleted')

class ExportMixin:
    # Placeholder for export functionality
    pass

class ReadOnlyMixin:
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class BaseAdmin(admin.ModelAdmin, SearchMixin, FilterMixin):
    list_display = ('id', 'created_at', 'is_active', 'is_deleted')
    readonly_fields = ('id', 'created_at', 'updated_at', 'deleted_at')
