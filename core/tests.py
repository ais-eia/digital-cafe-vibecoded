from decimal import Decimal
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.test.utils import override_script_prefix
from django.urls import NoReverseMatch, get_script_prefix, reverse

from .models import CartItem, Product, Transaction, TransactionLineItem
from .utils import redirect_without_script_prefix


class ProductAdminTests(TestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_superuser(
            username='admin-user',
            password='admin-password',
        )
        self.user = get_user_model().objects.create_user(username='regular-user')
        self.product = Product.objects.create(name='House Blend', price=Decimal('3.50'))

    def test_product_is_registered_with_expected_admin_configuration(self):
        product_admin = admin.site._registry[Product]

        self.assertEqual(product_admin.list_display, ('name', 'price'))
        self.assertEqual(product_admin.search_fields, ('name',))

    def test_staff_user_can_access_product_admin(self):
        self.client.force_login(self.staff)

        response = self.client.get('/admin/core/product/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House Blend')

    def test_non_staff_user_is_denied_product_admin(self):
        self.client.force_login(self.user)

        response = self.client.get('/admin/core/product/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_anonymous_user_is_redirected_to_admin_login(self):
        response = self.client.get('/admin/core/product/')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])

    def test_staff_can_create_product(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            '/admin/core/product/add/',
            {'name': 'Cappuccino', 'price': '4.75', '_save': 'Save'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Product.objects.filter(name='Cappuccino', price=Decimal('4.75')).exists())

    def test_staff_can_edit_product(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            f'/admin/core/product/{self.product.pk}/change/',
            {'name': 'Renamed Coffee', 'price': '9.99', '_save': 'Save'},
        )

        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Renamed Coffee')
        self.assertEqual(self.product.price, Decimal('9.99'))

    def test_invalid_admin_price_is_rejected(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            f'/admin/core/product/{self.product.pk}/change/',
            {'name': 'House Blend', 'price': '-1.00', '_save': 'Save'},
        )

        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal('3.50'))
        self.assertContains(response, 'Ensure this value is greater than or equal to 0.')

    def test_product_search_finds_matching_name(self):
        Product.objects.create(name='Cappuccino', price=Decimal('4.75'))
        self.client.force_login(self.staff)

        response = self.client.get('/admin/core/product/', {'q': 'Cappuccino'})

        self.assertContains(response, 'Cappuccino')
        self.assertNotContains(response, 'House Blend')

    def test_staff_can_delete_unprotected_product(self):
        self.client.force_login(self.staff)

        response = self.client.post(
            f'/admin/core/product/{self.product.pk}/delete/',
            {'post': 'yes'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_protected_delete_shows_clear_error_and_preserves_product(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)
        self.client.force_login(self.staff)

        confirmation = self.client.get(f'/admin/core/product/{self.product.pk}/delete/')

        self.assertEqual(confirmation.status_code, 200)
        self.assertContains(confirmation, 'Cannot delete product')
        self.assertContains(confirmation, 'Cart item:')

        response = self.client.post(
            f'/admin/core/product/{self.product.pk}/delete/',
            {'post': 'yes'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cannot delete product')
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_admin_edit_does_not_change_transaction_snapshot(self):
        purchase = Transaction.objects.create(user=self.user, total=Decimal('3.50'))
        TransactionLineItem.objects.create(
            transaction=purchase,
            product=self.product,
            product_name='House Blend',
            unit_price=Decimal('3.50'),
            quantity=1,
        )
        self.client.force_login(self.staff)

        self.client.post(
            f'/admin/core/product/{self.product.pk}/change/',
            {'name': 'Renamed Coffee', 'price': '9.99', '_save': 'Save'},
        )

        self.client.force_login(self.user)
        response = self.client.get('/transactions/')
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertNotContains(response, 'Renamed Coffee')
        self.assertNotContains(response, '$9.99')

    def test_admin_delete_nulls_transaction_product_and_preserves_snapshot(self):
        purchase = Transaction.objects.create(user=self.user, total=Decimal('3.50'))
        line_item = TransactionLineItem.objects.create(
            transaction=purchase,
            product=self.product,
            product_name='House Blend',
            unit_price=Decimal('3.50'),
            quantity=1,
        )
        self.client.force_login(self.staff)

        response = self.client.post(
            f'/admin/core/product/{self.product.pk}/delete/',
            {'post': 'yes'},
        )

        self.assertEqual(response.status_code, 302)
        line_item.refresh_from_db()
        self.assertIsNone(line_item.product)
        self.assertEqual(line_item.product_name, 'House Blend')
        self.assertEqual(line_item.unit_price, Decimal('3.50'))

    def test_public_catalog_shows_admin_created_product(self):
        self.client.force_login(self.staff)
        self.client.post(
            '/admin/core/product/add/',
            {'name': 'Admin Coffee', 'price': '5.25', '_save': 'Save'},
        )

        response = self.client.get('/')

        self.assertContains(response, 'Admin Coffee')


@override_settings(
    FORCE_SCRIPT_NAME='',
    LOGIN_URL='/login/',
    LOGIN_REDIRECT_URL='/',
)
@override_script_prefix('/')
class AuthNavigationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='nav-user')
        self.product = Product.objects.create(name='House Blend', price=Decimal('3.50'))
        self.client.force_login(self.user)

    def test_authenticated_pages_show_navigation_and_logout_form(self):
        urls = [
            reverse('home'),
            reverse('product-detail', args=[self.product.pk]),
            reverse('cart'),
            reverse('checkout'),
            reverse('transaction-history'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'data-auth-navigation')
                self.assertContains(response, 'Signed in as nav-user')
                self.assertContains(response, 'method="post"')
                self.assertContains(response, f'action="{reverse("logout")}"')
                self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_checkout_confirmation_shows_navigation(self):
        purchase = Transaction.objects.create(user=self.user, total=Decimal('3.50'))

        response = self.client.get(reverse('checkout-complete', args=[purchase.pk]))

        self.assertContains(response, 'data-auth-navigation')
        self.assertContains(response, 'View transaction history')

    def test_login_page_hides_authenticated_navigation(self):
        self.client.logout()

        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'data-auth-navigation')
        self.assertNotContains(response, 'Signed in as')
        self.assertNotContains(response, 'data-auth-navigation')

    def test_logout_post_redirects_and_invalidates_session(self):
        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, '/login/')
        protected_response = self.client.get(reverse('home'))
        self.assertRedirects(protected_response, '/login/?next=/')

    def test_logout_get_does_not_log_out(self):
        response = self.client.get(reverse('logout'))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)

    @override_settings(FORCE_SCRIPT_NAME='/proxy/8000')
    @override_script_prefix('/proxy/8000')
    def test_navigation_links_and_logout_action_include_proxy_prefix(self):
        response = self.client.get('/', SCRIPT_NAME='/proxy/8000')

        self.assertContains(response, 'href="/proxy/8000/"')
        self.assertContains(response, 'action="/proxy/8000/logout/"')


@override_settings(
    FORCE_SCRIPT_NAME='',
    LOGIN_URL='/login/',
    LOGIN_REDIRECT_URL='/',
)
@override_script_prefix('/')
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

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("home")}',
        )

    def test_login_page_displays_authentication_form(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': 'wrong-password'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password.')

    def test_valid_credentials_redirect_to_home_and_greet_user(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': self.password},
        )

        self.assertRedirects(response, reverse('home'))
        home_response = self.client.get(reverse('home'))
        self.assertEqual(home_response.status_code, 200)
        self.assertContains(home_response, f'Welcome, {self.username}!')

    def test_authenticated_user_can_access_home(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('home'))

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


@override_settings(
    FORCE_SCRIPT_NAME='',
    LOGIN_URL='/login/',
    LOGIN_REDIRECT_URL='/',
)
@override_script_prefix('/')
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

        self.assertContains(response, f'href="{reverse("product-detail", args=[self.product.pk])}"')

    def test_product_detail_displays_name_price_and_home_link(self):
        response = self.client.get(reverse('product-detail', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertContains(response, f'href="{reverse("home")}"')

    def test_unknown_product_returns_not_found(self):
        response = self.client.get(reverse('product-detail', args=[9999]))

        self.assertEqual(response.status_code, 404)

    def test_empty_catalog_shows_message(self):
        Product.objects.all().delete()

        response = self.client.get(reverse('home'))

        self.assertContains(response, 'No coffee products are available yet.')

    def test_anonymous_user_is_redirected_from_product_detail(self):
        self.client.logout()

        response = self.client.get(reverse('product-detail', args=[self.product.pk]))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("product-detail", args=[self.product.pk])}',
        )


@override_settings(
    FORCE_SCRIPT_NAME='',
    LOGIN_URL='/login/',
    LOGIN_REDIRECT_URL='/',
)
@override_script_prefix('/')
class ShoppingCartTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='customer')
        self.other_user = get_user_model().objects.create_user(username='other')
        self.product = Product.objects.create(name='House Blend', price=Decimal('3.50'))
        self.client.force_login(self.user)

    def test_product_detail_renders_quantity_form_and_csrf_token(self):
        response = self.client.get(reverse('product-detail', args=[self.product.pk]))

        self.assertContains(response, f'action="{reverse("product-detail", args=[self.product.pk])}"')
        self.assertContains(response, 'name="quantity"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_valid_add_creates_cart_item_and_redirects_to_cart(self):
        response = self.client.post(
            reverse('product-detail', args=[self.product.pk]),
            {'quantity': 3},
        )

        self.assertRedirects(response, '/cart/')
        item = CartItem.objects.get(user=self.user, product=self.product)
        self.assertEqual(item.quantity, 3)

    def test_repeated_add_increments_existing_cart_item(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=4)

        response = self.client.post(
            reverse('product-detail', args=[self.product.pk]),
            {'quantity': 3},
        )

        self.assertRedirects(response, '/cart/')
        self.assertEqual(CartItem.objects.get(user=self.user, product=self.product).quantity, 7)
        self.assertEqual(CartItem.objects.filter(user=self.user, product=self.product).count(), 1)

    def test_add_over_maximum_does_not_change_existing_quantity(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=98)

        response = self.client.post(
            reverse('product-detail', args=[self.product.pk]),
            {'quantity': 2},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cannot exceed 99')
        self.assertEqual(CartItem.objects.get(user=self.user, product=self.product).quantity, 98)

    def test_invalid_quantities_do_not_create_cart_items(self):
        for quantity in ('', '0', '-1', '1.5', '100', 'not-a-number'):
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    reverse('product-detail', args=[self.product.pk]),
                    {'quantity': quantity},
                )

                self.assertEqual(response.status_code, 200)
                self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_get_does_not_mutate_cart(self):
        response = self.client.get(reverse('product-detail', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_cart_displays_current_users_items_and_line_total(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=3)
        CartItem.objects.create(
            user=self.other_user,
            product=self.product,
            quantity=7,
        )

        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertContains(response, '$10.50')
        self.assertContains(response, '>3<')
        self.assertNotContains(response, '>7<')

    def test_empty_cart_displays_message(self):
        response = self.client.get(reverse('cart'))

        self.assertContains(response, 'Your cart is empty.')

    def test_user_cannot_see_or_mutate_other_users_cart(self):
        CartItem.objects.create(user=self.other_user, product=self.product, quantity=5)

        response = self.client.get(reverse('cart'))

        self.assertContains(response, 'Your cart is empty.')
        self.assertNotContains(response, '>5<')
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_get_add_route_does_not_mutate_cart(self):
        response = self.client.get(reverse('product-detail', args=[self.product.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_product_cannot_be_deleted_while_in_a_cart(self):
        CartItem.objects.create(user=self.user, product=self.product, quantity=1)

        with self.assertRaises(ProtectedError):
            self.product.delete()

    def test_anonymous_user_is_redirected_from_cart_and_add(self):
        self.client.logout()

        cart_response = self.client.get(reverse('cart'))
        add_response = self.client.post(
            reverse('product-detail', args=[self.product.pk]),
            {'quantity': 1},
        )

        self.assertRedirects(
            cart_response,
            f'{reverse("login")}?next={reverse("cart")}',
        )
        self.assertRedirects(
            add_response,
            f'{reverse("login")}?next={reverse("product-detail", args=[self.product.pk])}',
        )


class ProxyPrefixTests(TestCase):
    @override_settings(
        FORCE_SCRIPT_NAME='/proxy/8000',
        LOGIN_URL='/proxy/8000/login/',
        LOGIN_REDIRECT_URL='/proxy/8000/',
    )
    @override_script_prefix('/proxy/8000')
    def test_default_proxy_prefix_is_used_for_reversed_urls(self):
        self.assertEqual(reverse('home'), '/proxy/8000/')
        self.assertEqual(reverse('login'), '/proxy/8000/login/')
        self.assertEqual(reverse('product-detail', args=[2]), '/proxy/8000/products/2/')

    @override_script_prefix('/')
    def test_empty_proxy_prefix_supports_direct_local_urls(self):
        self.assertEqual(reverse('home'), '/')
        self.assertEqual(reverse('login'), '/login/')
        self.assertEqual(reverse('product-detail', args=[2]), '/products/2/')

    @override_settings(FORCE_SCRIPT_NAME='/proxy/8000')
    @override_script_prefix('/proxy/8000')
    def test_redirect_helper_omits_prefix_and_restores_it(self):
        response = redirect_without_script_prefix('cart')

        self.assertEqual(response['Location'], '/cart/')
        self.assertEqual(get_script_prefix(), '/proxy/8000/')

    @override_settings(FORCE_SCRIPT_NAME='/proxy/8000')
    @override_script_prefix('/proxy/8000')
    def test_redirect_helper_restores_prefix_after_reverse_failure(self):
        with self.assertRaises(NoReverseMatch):
            redirect_without_script_prefix('missing-route')

        self.assertEqual(get_script_prefix(), '/proxy/8000/')

    @override_settings(
        FORCE_SCRIPT_NAME='/proxy/8000',
        LOGIN_URL='/login/',
        LOGIN_REDIRECT_URL='/',
    )
    def test_authentication_redirect_targets_are_unprefixed(self):
        self.assertEqual(settings.LOGIN_URL, '/login/')
        self.assertEqual(settings.LOGIN_REDIRECT_URL, '/')


@override_settings(
    FORCE_SCRIPT_NAME='',
    LOGIN_URL='/login/',
    LOGIN_REDIRECT_URL='/',
)
@override_script_prefix('/')
class CheckoutTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='buyer')
        self.other_user = get_user_model().objects.create_user(username='other-buyer')
        self.product = Product.objects.create(name='House Blend', price=Decimal('3.50'))
        self.other_product = Product.objects.create(name='Cappuccino', price=Decimal('4.75'))
        self.client.force_login(self.user)
        self.item = CartItem.objects.create(user=self.user, product=self.product, quantity=2)

    def test_checkout_displays_editable_items_and_total(self):
        response = self.client.get(reverse('checkout'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertContains(response, 'value="2"')
        self.assertContains(response, '$7.00')
        self.assertContains(response, 'value="complete"')
        self.assertContains(response, f'action="{reverse("checkout")}"')

    def test_checkout_updates_quantity(self):
        response = self.client.post(
            reverse('checkout'),
            {'action': 'update', 'item_id': self.item.pk, 'quantity': 5},
        )

        self.assertRedirects(response, '/checkout/')
        self.assertEqual(CartItem.objects.get(pk=self.item.pk).quantity, 5)

    def test_checkout_removes_item(self):
        response = self.client.post(
            reverse('checkout'),
            {'action': 'remove', 'item_id': self.item.pk},
        )

        self.assertRedirects(response, '/checkout/')
        self.assertFalse(CartItem.objects.filter(pk=self.item.pk).exists())

    def test_invalid_checkout_quantity_does_not_change_cart(self):
        for quantity in ('0', '-1', '1.5', '100', 'not-a-number'):
            with self.subTest(quantity=quantity):
                response = self.client.post(
                    reverse('checkout'),
                    {'action': 'update', 'item_id': self.item.pk, 'quantity': quantity},
                )

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'errorlist')
                self.assertEqual(CartItem.objects.get(pk=self.item.pk).quantity, 2)

    def test_checkout_isolates_cart_items_by_user(self):
        other_item = CartItem.objects.create(
            user=self.other_user,
            product=self.other_product,
            quantity=4,
        )

        response = self.client.post(
            reverse('checkout'),
            {'action': 'remove', 'item_id': other_item.pk},
        )

        self.assertRedirects(response, '/checkout/')
        self.assertTrue(CartItem.objects.filter(pk=other_item.pk).exists())

    def test_successful_checkout_creates_snapshots_total_and_clears_cart(self):
        response = self.client.post(reverse('checkout'), {'action': 'complete'})

        purchase = Transaction.objects.get(user=self.user)
        line_item = purchase.line_items.get()
        self.assertRedirects(response, f'/checkout/complete/{purchase.pk}/')
        self.assertEqual(purchase.total, Decimal('7.00'))
        self.assertEqual(line_item.product, self.product)
        self.assertEqual(line_item.product_name, 'House Blend')
        self.assertEqual(line_item.unit_price, Decimal('3.50'))
        self.assertEqual(line_item.quantity, 2)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_checkout_ignores_submitted_prices_and_totals(self):
        response = self.client.post(
            reverse('checkout'),
            {'action': 'complete', 'price': '0.01', 'total': '0.01'},
        )

        self.assertRedirects(response, f'/checkout/complete/{Transaction.objects.get().pk}/')
        self.assertEqual(Transaction.objects.get().total, Decimal('7.00'))

    def test_checkout_snapshots_survive_product_change_and_delete(self):
        self.client.post(reverse('checkout'), {'action': 'complete'})
        purchase = Transaction.objects.get(user=self.user)
        self.product.name = 'Renamed Coffee'
        self.product.price = Decimal('9.99')
        self.product.save()
        line_item = purchase.line_items.get()

        self.assertEqual(line_item.product_name, 'House Blend')
        self.assertEqual(line_item.unit_price, Decimal('3.50'))
        self.product.delete()
        line_item.refresh_from_db()
        self.assertIsNone(line_item.product)
        self.assertEqual(line_item.product_name, 'House Blend')

    def test_empty_checkout_does_not_create_transaction(self):
        CartItem.objects.filter(user=self.user).delete()

        response = self.client.post(reverse('checkout'), {'action': 'complete'})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your checkout is empty.')
        self.assertFalse(Transaction.objects.exists())

    @patch('core.views.TransactionLineItem.objects.bulk_create')
    def test_checkout_rolls_back_when_line_creation_fails(self, bulk_create):
        bulk_create.side_effect = RuntimeError('line creation failed')

        with self.assertRaises(RuntimeError):
            self.client.post(reverse('checkout'), {'action': 'complete'})

        self.assertFalse(Transaction.objects.exists())
        self.assertTrue(CartItem.objects.filter(pk=self.item.pk).exists())

    def test_completion_page_is_private(self):
        self.client.post(reverse('checkout'), {'action': 'complete'})
        purchase = Transaction.objects.get(user=self.user)
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse('checkout-complete', args=[purchase.pk]),
        )

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_is_redirected_from_checkout(self):
        self.client.logout()

        response = self.client.get(reverse('checkout'))

        self.assertRedirects(response, f'/login/?next=/checkout/')


@override_settings(
    FORCE_SCRIPT_NAME='',
    LOGIN_URL='/login/',
    LOGIN_REDIRECT_URL='/',
)
@override_script_prefix('/')
class TransactionHistoryTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='history-user')
        self.other_user = get_user_model().objects.create_user(username='other-history-user')
        self.product = Product.objects.create(name='House Blend', price=Decimal('3.50'))
        self.client.force_login(self.user)

    def create_transaction(self, user=None, product_name='House Blend', unit_price='3.50'):
        purchase = Transaction.objects.create(
            user=user or self.user,
            total=Decimal(unit_price) * 2,
        )
        TransactionLineItem.objects.create(
            transaction=purchase,
            product=self.product,
            product_name=product_name,
            unit_price=Decimal(unit_price),
            quantity=2,
        )
        return purchase

    def test_empty_history_displays_message(self):
        response = self.client.get(reverse('transaction-history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No purchases yet.')

    def test_history_displays_current_users_transactions_newest_first(self):
        older = self.create_transaction(product_name='Older Coffee')
        newer = self.create_transaction(product_name='Newer Coffee')
        Transaction.objects.filter(pk=older.pk).update(created_at='2020-01-01T00:00:00Z')
        Transaction.objects.filter(pk=newer.pk).update(created_at='2024-01-01T00:00:00Z')
        self.create_transaction(user=self.other_user, product_name='Other User Coffee')

        response = self.client.get(reverse('transaction-history'))

        self.assertContains(response, 'Older Coffee')
        self.assertContains(response, 'Newer Coffee')
        self.assertNotContains(response, 'Other User Coffee')
        self.assertLess(
            response.content.index(b'Newer Coffee'),
            response.content.index(b'Older Coffee'),
        )

    def test_history_renders_original_snapshots_after_product_changes(self):
        self.create_transaction()
        self.product.name = 'Renamed Coffee'
        self.product.price = Decimal('9.99')
        self.product.save()

        response = self.client.get(reverse('transaction-history'))

        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')
        self.assertNotContains(response, 'Renamed Coffee')
        self.assertNotContains(response, '$9.99')

    def test_history_renders_original_snapshots_after_product_deletion(self):
        self.create_transaction()
        self.product.delete()

        response = self.client.get(reverse('transaction-history'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'House Blend')
        self.assertContains(response, '$3.50')

    def test_history_link_is_prefix_aware(self):
        response = self.client.get(reverse('transaction-history'))

        self.assertContains(response, f'href="{reverse("home")}"')

    def test_anonymous_user_is_redirected_from_history(self):
        self.client.logout()

        response = self.client.get(reverse('transaction-history'))

        self.assertRedirects(response, '/login/?next=/transactions/')
