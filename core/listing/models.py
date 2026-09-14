from datetime import timezone

from categories.models import Category
from django.db import models
from django.db.models import ForeignKey
from users.models import User
from utils.base_model import BaseModel


class Listing(BaseModel):
    seller = ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    images = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-creation_date']