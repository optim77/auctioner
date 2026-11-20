from django.contrib.postgres.indexes import GinIndex
from django.db import models
from utils.base_model import BaseModel


class Category(BaseModel):
    name = models.CharField()
    description = models.TextField(blank=True, null=True)
    items_amount = models.IntegerField(default=0)
    icon = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            GinIndex(
                fields=["name"],
                opclasses=["gin_trgm_ops"],
                name="category_name_trgm_idx",
            ),
        ]

    def __str__(self):
        return self.name
