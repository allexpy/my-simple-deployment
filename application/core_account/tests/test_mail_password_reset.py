from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from django.test import TestCase


class PasswordResetMailTests(TestCase):

    def setUp(self):
        get_user_model().objects.create(username='john', email='john@doe.com', password='123abcdef')
        self.url = reverse('password_reset')
        self.response = self.client.post(self.url, {'email': 'john@doe.com'})
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEqual('[Django Boards] Please reset your password', self.email.subject)

    def test_email_body(self):
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('john', self.email.body)
        self.assertIn('john@doe.com', self.email.body)

    def test_email_to(self):
        self.assertEqual(['john@doe.com', ], self.email.to)
