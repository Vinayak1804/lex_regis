from rest_framework.permissions import BasePermission

class CanUploadDocument(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class CanViewDocument(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True 
