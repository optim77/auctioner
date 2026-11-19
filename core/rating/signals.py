from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from rating.models import Rating


def _mark_rating_dirty(rated_user) -> None:
    if rated_user is None:
        return
    type(rated_user).objects.filter(id=rated_user.id).update(sum_user_rating=True)


@receiver(post_save, sender=Rating)
def mark_rating_dirty_on_save(sender, instance, **kwargs) -> None:
    """Recompute the average after a rating is created or edited."""
    _mark_rating_dirty(instance.rated_user)


@receiver(post_delete, sender=Rating)
def mark_rating_dirty_on_delete(sender, instance, **kwargs) -> None:
    """Recompute the average after a rating is removed."""
    _mark_rating_dirty(instance.rated_user)
