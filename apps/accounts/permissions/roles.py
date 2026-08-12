from rest_framework.permissions import BasePermission
from apps.common.choices.system import RoleChoices

class IsVerifiedLawyer(BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == RoleChoices.LAWYER):
            return False
        return getattr(request.user, 'lawyer_profile', None) and request.user.lawyer_profile.verification_status == 'VERIFIED'

class IsCitizen(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == RoleChoices.CITIZEN)

class IsAdministrator(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, 'role', None) == RoleChoices.ADMIN)

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or getattr(obj, 'user', None) == request.user
