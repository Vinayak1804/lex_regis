from django.utils.text import slugify

def generate_slug(text: str) -> str:
    return slugify(text)

def format_response(data, message="Success", success=True):
    return {
        "success": success,
        "message": message,
        "data": data
    }
