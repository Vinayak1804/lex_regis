import logging
from functools import wraps

logger = logging.getLogger('apps')

def audit_log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Execution started for {func.__name__} with args={args} kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Execution successful for {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Execution failed for {func.__name__}: {str(e)}")
            raise
    return wrapper
