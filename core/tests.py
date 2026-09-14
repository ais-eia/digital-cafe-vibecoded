from django.contrib.auth import get_user_model
from django.test import TestCase


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
