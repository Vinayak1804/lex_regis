def is_htmx(request):
    """
    Safely check if the request is an HTMX request.
    This avoids relying on `request.htmx` which can cause runtime errors
    if django-htmx middleware is not loaded or configured incorrectly.
    """
    if hasattr(request, 'htmx') and bool(request.htmx):
        return True
    return request.headers.get('HX-Request') == 'true'
