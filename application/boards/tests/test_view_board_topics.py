from django.test import TestCase
from django.urls import reverse, resolve

from boards.models import Board
from boards.views import BoardTopicsView


class BoardTopicsTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.response = self.client.get(self.url)

    def test_board_topics_view_success_status_code(self):
        """
        Checks url status code when accessing it.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        """
        Checks if url gives 404 status code when trying to access an instance that doesn't exist.
        """
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_board_topics_url_resolves_board_topics_view(self):
        """
        Checks if url uses this view.
        """
        view = resolve('/boards/1/')
        self.assertEqual(view.func.view_class, BoardTopicsView)

    def test_board_topics_view_contains_link_back_to_page(self):
        """
        Check if response contains a link with the homepage_url target.
        """
        homepage_url = reverse('home')
        self.assertContains(self.response, 'href="{0}"'.format(homepage_url))

    def test_board_topics_view_contains_navigation_links(self):
        """
        Check if response contains navigation links with the homepage_url target.
        """
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(homepage_url))
        self.assertContains(self.response, 'href="{0}"'.format(new_topic_url))
