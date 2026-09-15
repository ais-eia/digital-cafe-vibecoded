from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )

    class Meta:
        ordering = ['name', 'pk']

    def __str__(self):
        return self.name
