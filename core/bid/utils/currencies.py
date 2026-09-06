from django.db import models


class Currency(models.TextChoices):
    PLN = "PLN", "Polish Złoty"
    EUR = "EUR", "Euro"
    USD = "USD", "US Dollar"