from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.test import TestCase
from django.urls import reverse, resolve

from core_account.forms import SignUpForm
from core_account.views import SignUpView


class SignUpTests(TestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.response = self.client.get(self.url)

    def test_signup_status_code(self):
        """
        Checks url status code when accessing it.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/signup')
        self.assertEqual(view.func.view_class, SignUpView)

    def test_csrf(self):
        """
        Checks if form contains csrf token.
        """
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """
        Checks if form exists in template.
        """
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

    def test_form_inputs(self):
        """
        The view must contain five inputs: csrf, username, email, password1, password2.
        """
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignUpTests(TestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.home_url = reverse('home')
        data = dict()
        data['username'] = 'Jhon'
        data['email'] = 'jhon@doe.com'
        data['password1'] = 'abcdef123456'
        data['password2'] = 'abcdef123456'
        self.response = self.client.post(self.url, data)

    def test_redirection(self):
        """
        A valid form submission should redirect the user to the home page.
        """
        self.assertRedirects(self.response, self.home_url)

    def test_user_authentication(self):
        """
        Create a new request to an arbitrary page. The resulting response should now have a `user` to its context, after a successful sign up.
        """
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):

    def setUp(self):
        self.url = reverse('signup')
        self.response = self.client.post(self.url, {})

    def test_signup_status_code(self):
        """
        An invalid form submission should return to the same page.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        """
        Checks if form errors exists.
        """
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        """
        Checks if user wasn't created.
        """
        self.assertFalse(get_user_model().objects.exists())
