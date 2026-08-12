from rest_framework.response import Response
from rest_framework import status

class SuccessResponse(Response):
    def __init__(self, data=None, message="Success", **kwargs):
        payload = {"success": True, "message": message, "data": data}
        super().__init__(data=payload, status=status.HTTP_200_OK, **kwargs)

class ValidationErrorResponse(Response):
    def __init__(self, errors=None, message="Validation Error", **kwargs):
        payload = {"success": False, "message": message, "errors": errors}
        super().__init__(data=payload, status=status.HTTP_400_BAD_REQUEST, **kwargs)

class NotFoundResponse(Response):
    def __init__(self, message="Not Found", **kwargs):
        payload = {"success": False, "message": message}
        super().__init__(data=payload, status=status.HTTP_404_NOT_FOUND, **kwargs)

class ServerErrorResponse(Response):
    def __init__(self, message="Internal Server Error", **kwargs):
        payload = {"success": False, "message": message}
        super().__init__(data=payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR, **kwargs)
