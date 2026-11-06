from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    if isinstance(exc, ObjectDoesNotExist):
        exc = NotFound()

    return exception_handler(exc, context)
