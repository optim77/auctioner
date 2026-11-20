"""Minimal, dependency-free CORS support.

Only origins explicitly listed in ``CORS_ALLOWED_ORIGINS`` are accepted; the
``Origin`` header is never echoed blindly. Preflight requests are answered
before authentication so browsers can send Authorization/Content-Type.
"""
from django.conf import settings
from django.http import HttpResponse


class CorsMiddleware:
    _ALLOWED_METHODS = "GET, POST, PUT, PATCH, DELETE, OPTIONS"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get("HTTP_ORIGIN")
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        is_preflight = (
            request.method == "OPTIONS"
            and "HTTP_ACCESS_CONTROL_REQUEST_METHOD" in request.META
        )

        response = (
            HttpResponse(status=204)
            if is_preflight and origin in allowed_origins
            else self.get_response(request)
        )

        if origin and origin in allowed_origins:
            response["Access-Control-Allow-Origin"] = origin
            response.headers.add("Vary", "Origin")
            response["Access-Control-Allow-Credentials"] = "true"

            if is_preflight:
                response["Access-Control-Allow-Methods"] = self._ALLOWED_METHODS
                response["Access-Control-Allow-Headers"] = (
                    request.META.get("HTTP_ACCESS_CONTROL_REQUEST_HEADERS")
                    or "Authorization, Content-Type"
                )
                response["Access-Control-Max-Age"] = "86400"

        return response
