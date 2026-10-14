from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from auction.rules import InvalidAuctionTransition

def custom_exception_handler(exc, context):
    if isinstance(exc, InvalidAuctionTransition):
        exc = ValidationError({"detail": str(exc)})
    return exception_handler(exc, context)