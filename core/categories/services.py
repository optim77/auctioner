from uuid import UUID

from django.db.models import F

from categories.models import Category


def increment_category_items_count(category_id: UUID) -> None:
    Category.objects.filter(id=category_id).update(
        items_amount=F('items_amount') + 1
    )

def decrement_category_items_count(category_id: UUID) -> None:
    Category.objects.filter(id=category_id).update(
        items_amount=F('items_amount') - 1
    )