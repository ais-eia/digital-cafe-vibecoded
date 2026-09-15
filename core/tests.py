from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Product


class AuthenticationTests(TestCase):
    def setUp(self):
        self.username = 'barista'
        self.password = 'strong-password-123'
        self.user = get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_anonymous_home_redirects_to_login(self):
        response = self.client.get('/')

        self.assertRedirects(response, '/login/?next=/')

    def test_login_page_displays_authentication_form(self):
        response = self.client.get('/login/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            '/login/',
            {'username': self.username, 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_valid_credentials_redirect_to_home_and_greet_user(self):
        response = self.client.post(
            '/login/',
            {'username': self.username, 'password': self.password},
        )

        self.assertRedirects(response, '/')
        home_response = self.client.get('/')
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, f'Welcome, {self.username}!')

    def test_authenticated_user_can_access_home(self):
        self.client.force_login(self.user)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)


class ProductModelTests(TestCase):
    def test_product_preserves_decimal_price(self):
        product = Product.objects.create(name='Espresso', price=Decimal('2.50'))

        self.assertEqual(product.price, Decimal('2.50'))

    def test_product_rejects_negative_price(self):
        product = Product(name='Invalid Coffee', price=Decimal('-1.00'))

        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_products_are_ordered_by_name_then_primary_key(self):
        first = Product.objects.create(name='Latte', price=Decimal('4.00'))
        second = Product.objects.create(name='Americano', price=Decimal('3.00'))
        third = Product.objects.create(name='Latte', price=Decimal('4.50'))

        self.assertEqual(list(Product.objects.all()), [second, first, third])


class ProductBrowsingTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='customer',
            password='strong-password-123',
        )
        self.client.force_login(self.user)
        self.product = Product.objects.create(
            name='House Blend',
            price=Decimal('3.50'),
        )
        self.other_product = Product.objects.create(
            name='Cappuccino',
            price=Decimal('4.75'),
        )

    def test_home_lists_products_and_preserves_greeting(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome, customer!')
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertContains(response, 'Cappuccino')
        self.assertContains(response, '$4.75')

    def test_home_products_are_ordered_by_name(self):
        response = self.client.get('/')

        self.assertLess(
            response.content.index(b'Cappuccino'),
            response.content.index(b'House Blend'),
        )

    def test_home_links_product_name_to_detail_page(self):
        response = self.client.get('/')

        self.assertContains(response, f'href="/products/{self.product.pk}/"')

    def test_product_detail_displays_name_price_and_home_link(self):
        response = self.client.get(f'/products/{self.product.pk}/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertContains(response, 'href="/"')

    def test_unknown_product_returns_not_found(self):
        response = self.client.get('/products/9999/')

        self.assertEqual(response.status_code, 404)

    def test_empty_catalog_shows_message(self):
        Product.objects.all().delete()

        response = self.client.get('/')

        self.assertContains(response, 'No coffee products are available yet.')

    def test_anonymous_user_is_redirected_from_product_detail(self):
        self.client.logout()

        response = self.client.get(f'/products/{self.product.pk}/')

        self.assertRedirects(response, f'/login/?next=/products/{self.product.pk}/')
