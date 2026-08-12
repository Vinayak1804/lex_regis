from rest_framework import viewsets
from rest_framework.decorators import action
from apps.common.api.responses import SuccessResponse, ValidationErrorResponse
from .serializers import UserSerializer, RegistrationSerializer

class AuthViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            return SuccessResponse(message="User registered successfully")
        return ValidationErrorResponse(errors=serializer.errors)
        
    @action(detail=False, methods=['post'])
    def login(self, request):
        return SuccessResponse(message="Login successful")
        
    @action(detail=False, methods=['post'])
    def logout(self, request):
        return SuccessResponse(message="Logout successful")

class ProfileViewSet(viewsets.ViewSet):
    def list(self, request):
        return SuccessResponse(data=[])
