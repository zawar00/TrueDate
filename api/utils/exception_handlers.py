import logging
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, PermissionDenied, NotAuthenticated
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from .responses import error_response
from django.conf import settings

# Set up logger
logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler to get the standard error response.
    response = exception_handler(exc, context)

    # Log the error for debugging purposes
    view = context.get('view', None)
    request = context.get('request', None)
    logger.error(f"Error occurred in view: {view.__class__.__name__ if view else 'Unknown'}, "
                 f"method: {request.method if request else 'Unknown'}, exception: {str(exc)}")

    # If a response is generated by DRF
    if response is not None:
        errors = response.data
        message = errors.pop('detail', 'An error occurred') if 'detail' in errors else 'Validation errors'

        # Customize error messages based on the exception type
        if isinstance(exc, ValidationError):
            message = 'Validation failed'
        elif isinstance(exc, AuthenticationFailed):
            message = 'Authentication failed'
        elif isinstance(exc, PermissionDenied):
            message = 'You do not have permission to perform this action'
        elif isinstance(exc, NotAuthenticated):
            message = 'Authentication credentials were not provided'
        elif isinstance(exc, Http404) or isinstance(exc, ObjectDoesNotExist):
            message = 'The requested resource was not found'

        # In debug mode, provide more detailed error information
        if settings.DEBUG:
            errors['exception'] = str(exc)  # Attach exception details for debugging purposes

        # Return the error response
        return error_response(message=message, errors=errors, status_code=response.status_code)

    # If no response was generated, return a default error response
    return error_response(message="An unexpected error occurred", status_code=500)
