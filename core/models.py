from decimal import Decimal

from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import Q


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


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
    )

    class Meta:
        ordering = ['product__name', 'pk']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_cart_item_user_product',
            ),
            models.CheckConstraint(
                condition=Q(quantity__gte=1) & Q(quantity__lte=99),
                name='cart_item_quantity_1_to_99',
            ),
        ]

    @property
    def line_total(self):
        return self.product.price * self.quantity
