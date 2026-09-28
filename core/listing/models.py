from categories.models import Category
from django.db import models
from django.db.models import ForeignKey, Q
from users.models import User
from utils.base_model import BaseModel

class ListingQuerySet(models.QuerySet):

    def search(self, query):
        lookup = (Q(name__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query))
        qs = self.filter(lookup)
        return qs

class Listing(BaseModel):
    seller = ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    images = models.JSONField(null=True, blank=True)

    objects = ListingQuerySet.as_manager()

    class Meta:
        ordering = ['-creation_date']