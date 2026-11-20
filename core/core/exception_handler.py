from django.core.exceptions import (
    ObjectDoesNotExist,
)
from django.core.exceptions import (
    PermissionDenied as DjangoPermissionDenied,
)
from django.core.exceptions import (
    ValidationError as DjangoValidationError,
)
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Translate Django/database exceptions into predictable API responses."""
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound()
    elif isinstance(exc, DjangoValidationError):
        exc = ValidationError(exc.messages)
    elif isinstance(exc, ProtectedError):
        exc = APIException("Resource is still referenced and cannot be deleted.")
        exc.status_code = 409
    elif isinstance(exc, IntegrityError):
        exc = APIException("Conflicting data; the resource could not be saved.")
        exc.status_code = 409
    elif isinstance(exc, DjangoPermissionDenied):
        exc = PermissionDenied()

    return exception_handler(exc, context)
