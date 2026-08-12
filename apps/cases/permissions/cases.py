from rest_framework.permissions import BasePermission

class CanCreateCase(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class CanViewPrivateCase(BasePermission):
    def has_object_permission(self, request, view, obj):
        from apps.common.choices.system import RoleChoices
        if getattr(request.user, 'role', None) == RoleChoices.ADMIN:
            return True
        if getattr(obj.client, 'user', None) == request.user:
            return True
        if getattr(obj.assigned_lawyer, 'user', None) == request.user:
            return True
        return False
