from categories.models import Category
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import Q, QuerySet
from users.models import User
from utils.base_model import BaseModel


class ListingQuerySet(models.QuerySet):
    def search(self, query: str) -> QuerySet['Listing']:
        """Return listings matching name, description or category name."""
        lookup = (
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )
        return self.filter(lookup)


class Listing(BaseModel):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    images = models.JSONField(null=True, blank=True)

    objects = ListingQuerySet.as_manager()

    class Meta:
        ordering = ['-creation_date']
        indexes = [
            GinIndex(
                fields=['name'],
                opclasses=['gin_trgm_ops'],
                name='listing_name_trgm_idx',
            ),
            GinIndex(
                fields=['description'],
                opclasses=['gin_trgm_ops'],
                name='listing_description_trgm_idx',
            ),
        ]
