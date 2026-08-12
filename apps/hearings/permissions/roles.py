from apps.common.permissions.base import BasePermission

class HearingJudgePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.presiding_judge == request.user

class HearingCaseLawyerPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.case.assigned_lawyer == request.user

class HearingCourtAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'
