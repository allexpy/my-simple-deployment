from django.test import TestCase
from django.urls import reverse, resolve

from boards.models import Board
from boards.views import HomeView


class HomeTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('home')
        self.response = self.client.get(self.url)

    def test_home_view_status_code(self):
        """
        Checks url status code when accessing it.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/')
        self.assertEqual(view.func.view_class, HomeView)

    def test_home_view_contains_link_to_topics_page(self):
        """
        Check if response contains a link with the board_topics_url target.
        """
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))
