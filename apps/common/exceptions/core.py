from rest_framework.exceptions import APIException
from rest_framework import status

class BaseAppException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'An application error occurred.'
    default_code = 'error'

class ValidationException(BaseAppException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_code = 'validation_error'

class BusinessException(BaseAppException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_code = 'business_error'

class PermissionDeniedException(BaseAppException):
    status_code = status.HTTP_403_FORBIDDEN
    default_code = 'permission_denied'

class CaseException(BaseAppException):
    default_code = 'case_error'

class DocumentException(BaseAppException):
    default_code = 'document_error'

class AuthenticationException(BaseAppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'authentication_error'

class BlockchainException(BaseAppException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_code = 'blockchain_error'

class AIException(BaseAppException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_code = 'ai_error'

class PredictionException(BaseAppException):
    default_code = 'prediction_error'

class ResourceNotFoundException(BaseAppException):
    status_code = status.HTTP_404_NOT_FOUND
    default_code = 'not_found'
