from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from boards.forms import NewTopicForm, PostForm, PostUpdateForm
from .models import Board, Topic, Post


class HomeView(ListView):
    template_name = 'boards/boards.html'
    model = Board
    queryset = Board.objects.all()


class BoardTopicsView(DetailView):
    template_name = 'boards/topics.html'
    model = Board
    context_object_name = 'board'

    def get_object(self, queryset=None):
        return get_object_or_404(Board, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super(BoardTopicsView, self).get_context_data(**kwargs)
        context['topics'] = self.get_object().topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return context


class NewTopicView(LoginRequiredMixin, CreateView):
    template_name = 'boards/new_topic.html'
    model = Topic
    form_class = NewTopicForm

    def get_context_data(self, **kwargs):
        context = super(NewTopicView, self).get_context_data(**kwargs)
        context['board'] = get_object_or_404(Board, pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super(NewTopicView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['board'] = get_object_or_404(Board, pk=self.kwargs['pk'])
        return kwargs

    def form_valid(self, form):
        return super(NewTopicView, self).form_valid(form)

    def get_success_url(self):
        return reverse('topic_posts', kwargs={'pk': self.kwargs['pk'], 'topic_pk': self.object.pk})


class TopicPostsView(LoginRequiredMixin, DetailView):
    template_name = 'boards/topic_posts.html'
    model = Topic
    context_object_name = 'topic'

    def get_object(self, queryset=None):
        topic = get_object_or_404(Topic, board__pk=self.kwargs['pk'], pk=self.kwargs['topic_pk'])
        topic.views += 1
        topic.save()
        return topic


class ReplyTopicView(LoginRequiredMixin, CreateView):
    template_name = 'boards/reply_topic.html'
    model = Post
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super(ReplyTopicView, self).get_context_data(**kwargs)
        context['topic'] = get_object_or_404(Topic, board__pk=self.kwargs['pk'], pk=self.kwargs['topic_pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super(ReplyTopicView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['topic'] = get_object_or_404(Topic, board__pk=self.kwargs['pk'], pk=self.kwargs['topic_pk'])
        return kwargs

    def form_valid(self, form):
        return super(ReplyTopicView, self).form_valid(form)

    def get_success_url(self):
        return reverse('topic_posts', kwargs={'pk': self.kwargs['pk'], 'topic_pk': self.kwargs['topic_pk']})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostUpdateForm
    template_name = 'boards/edit_post.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Post, pk=self.kwargs['post_pk'], created_by=self.request.user)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        form.instance.updated_at = timezone.now()
        return super(PostUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('topic_posts', args=[self.get_object().topic.board.pk, self.get_object().topic.pk])
