from django.contrib.auth import views as auth_views, get_user_model
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import resolve, reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class PasswordResetTests(TestCase):

    def setUp(self):
        self.url = reverse('password_reset')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        """
        Checks url status code when accessing it.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/password_reset')
        self.assertEqual(view.func.view_class, auth_views.PasswordResetView)

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
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        """
        The view must contain two inputs: csrf and email.
        """
        self.assertContains(self.response, '<input', 2)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):

    def setUp(self):
        self.email = 'jhon@doe.com'
        self.url = reverse('password_reset')
        get_user_model().objects.create(username='john', email=self.email, password='123abcdef')
        self.response = self.client.post(self.url, {'email': self.email})

    def test_redirection(self):
        """
        A valid form submission should redirect the user to `password_reset_done` view.
        """
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        """
        A valid form submission of a valid email should sent an email.
        """
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):

    def setUp(self):
        self.email = 'donotexist@email.com'
        self.url = reverse('password_reset')
        self.response = self.client.post(self.url, {'email': self.email})

    def test_redirection(self):
        """
        Even invalid emails in the database should redirect the user to `password_reset_done` view.
        """
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self):
        """
        Checks if an email was sent.
        """
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):

    def setUp(self):
        self.url = reverse('password_reset_done')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        """
        Checks url status code when accessing it.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/password_reset/done')
        self.assertEqual(view.func.view_class, auth_views.PasswordResetDoneView)


class PasswordResetConfirmTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)
        self.url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(self.url, follow=True)

    def test_status_code(self):
        """
        Checks url status code.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/reset/{uid64}/{token}'.format(uid64=self.uid, token=self.token))
        self.assertEqual(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test_csrf(self):
        """
        Checks if form contains csrf token.
        """
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_forms(self):
        """
        Checks if form exists in template.
        """
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)

    def test_form_inputs(self):
        """
        The view must contain three inputs: csrf and new_password1 and new_password2.
        """
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='123abcdef')
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.token = default_token_generator.make_token(self.user)

        self.user.set_password('abcdef123')
        self.user.save()

        self.url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(self.url)

    def test_status_code(self):
        """
        Checks url status code.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_html(self):
        """
        Checks if password reset link is invalid and if exists.
        """
        password_reset_url = reverse('password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(self.response, 'href="{0}"'.format(password_reset_url))


class PasswordResetCompleteTests(TestCase):

    def setUp(self):
        self.url = reverse('password_reset_complete')
        self.response = self.client.get(self.url)

    def test_status_code(self):
        """
        Checks url status code.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/reset/done')
        self.assertEqual(view.func.view_class, auth_views.PasswordResetCompleteView)
