from channels.db import database_sync_to_async


class JWTAuthMiddleware:
    """Populate ``scope['user']`` from a Bearer token for WebSocket connects.

    Session authentication (via ``AuthMiddlewareStack``) is kept as a fallback;
    a valid JWT in the ``Authorization`` header takes precedence.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope["type"] == "websocket":
            headers = dict(scope.get("headers", []))
            authorization = headers.get(b"authorization", b"")
            if authorization.startswith(b"Bearer "):
                token = authorization.split(None, 1)[1].decode("utf-8")
                scope = {**scope, "user": await self._authenticate(token)}
        return await self.inner(scope, receive, send)

    @staticmethod
    @database_sync_to_async
    def _authenticate(token):
        from django.contrib.auth.models import AnonymousUser
        from rest_framework.exceptions import AuthenticationFailed
        from rest_framework_simplejwt.authentication import JWTAuthentication
        from rest_framework_simplejwt.exceptions import TokenError

        auth = JWTAuthentication()
        try:
            validated_token = auth.get_validated_token(token)
            return auth.get_user(validated_token)
        except (TokenError, AuthenticationFailed, ValueError):
            return AnonymousUser()
