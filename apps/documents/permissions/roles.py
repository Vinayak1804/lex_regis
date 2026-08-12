from apps.common.permissions.base import BasePermission

class DocumentOwnerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or obj.uploaded_by == request.user

class DocumentAssignedLawyerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.case.assigned_lawyer == request.user

class DocumentCourtPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.role == 'ADMIN'  # Assuming ADMIN acts as court or has court role

class DocumentVisibilityPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.visibility.code == 'PUBLIC':
            return True
        if obj.visibility.code == 'PRIVATE':
            return obj.owner == request.user or obj.uploaded_by == request.user
        if obj.visibility.code == 'RESTRICTED':
            return obj.case.assigned_lawyer == request.user or request.user.role == 'ADMIN'
        return False
