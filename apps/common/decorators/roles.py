from functools import wraps
from django.core.exceptions import PermissionDenied
from apps.common.choices.system import RoleChoices

def require_role(role_choice):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated or getattr(request.user, 'role', None) != role_choice:
                raise PermissionDenied(f"Required role: {role_choice}")
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_admin(func):
    return require_role(RoleChoices.ADMIN)(func)

def require_lawyer(func):
    return require_role(RoleChoices.LAWYER)(func)

def require_citizen(func):
    return require_role(RoleChoices.CITIZEN)(func)
