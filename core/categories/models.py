from django.db import models
from utils.base_model import BaseModel


class Category(BaseModel):
    name = models.CharField()
    description = models.TextField(blank=True, null=True)
    items_amount = models.IntegerField(blank=True, null=True)
    icon = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
