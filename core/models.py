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


class Transaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )

    class Meta:
        ordering = ['-created_at', '-pk']


class TransactionLineItem(models.Model):
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='line_items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transaction_line_items',
    )
    product_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
    )
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(99)],
    )

    class Meta:
        ordering = ['pk']
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gte=1) & Q(quantity__lte=99),
                name='transaction_line_item_quantity_1_to_99',
            ),
        ]

    @property
    def line_total(self):
        return self.unit_price * self.quantity
