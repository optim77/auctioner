from django.db import models
from django.db.models import ForeignKey

from categories.models import Category
from users.models import User
from utils.base_model import BaseModel


class Listing(BaseModel):
    seller = ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    creation_date = models.DateTimeField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    images = models.JSONField(null=True, blank=True)
