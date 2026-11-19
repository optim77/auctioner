from django.apps import AppConfig


class RatingConfig(AppConfig):
    name = 'rating'

    def ready(self) -> None:
        from rating import signals  # noqa: F401
