from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from boards.forms import NewTopicForm
from boards.models import Board, Topic, Post
from boards.views import NewTopicView


class NewTopicTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')
        self.url = reverse('new_topic', kwargs={'pk': self.board.pk})
        self.response = self.client.get(self.url)

    def test_new_topic_test_view(self):
        """
        Checks url status code when accessing it.
        """
        self.assertEquals(self.response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        """
        Checks if url gives 404 status code when trying to access an instance that doesn't exist.
        """
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolve_new_topic_view(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/boards/1/new')
        self.assertEquals(view.func.view_class, NewTopicView)

    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        """
        Check if response contains a link with the homepage_url target.
        """
        new_topic_url = reverse('new_topic', kwargs={'pk': self.board.pk})
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    def test_csrf(self):
        """
        Checks if form contains csrf token.
        """
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        """
        Checks if topic and post objects exists after the form post.
        """
        data = dict()
        data['subject'] = 'Test title'
        data['message'] = 'Lorem ipsum dolor sit amet'
        self.client.post(self.url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())

    def test_new_topic_invalid_post_data(self):
        """
        Invalid post data should not redirect. The expected behavior is to show the form again with validation errors.
        """
        response = self.client.post(self.url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        """
        Invalid post data should not redirect. The expected behavior is to show the form again with validation errors.
        """
        data = dict()
        data['subject'] = ''
        data['message'] = ''
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):
        """
        Checks if form exists in template.
        """
        form = self.response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)


class LoginRequiredNewTopicTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('new_topic', kwargs={'pk': self.board.pk})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
