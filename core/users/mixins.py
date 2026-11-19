class UserQueryMixin:
    """Restricts a viewset's queryset to objects related to the requesting user.

    ``user_field`` names the model attribute (e.g. ``user``, ``winner``).
    """

    user_field = "user"

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        return qs.filter(**{self.user_field: user})
