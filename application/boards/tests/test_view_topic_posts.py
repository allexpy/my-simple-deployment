from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from boards.models import Board, Post, Topic
from boards.views import TopicPostsView


class TopicPostsTests(TestCase):

    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=self.user)
        self.post = Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=self.user)
        self.url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.response = self.client.get(self.url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/')
        self.assertEqual(view.func.view_class, TopicPostsView)
