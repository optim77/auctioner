class UserQueryMixin:
    user_field = "user"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.user_field: self.request.user})
