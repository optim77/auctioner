from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.views import exception_handler
from auction.rules import InvalidAuctionTransition

def custom_exception_handler(exc, context):
    if isinstance(exc, InvalidAuctionTransition):
        exc = ValidationError({"detail": str(exc)})
    elif isinstance(exc, ObjectDoesNotExist):
        exc = NotFound()
    return exception_handler(exc, context)