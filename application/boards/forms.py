from django import forms
from django.utils import timezone

from .models import Topic, Post


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(max_length=4000, widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'What is on your mind?'}), help_text='The max length of the text is 4000.')

    class Meta:
        model = Topic
        fields = ['subject', 'message']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.board = kwargs.pop('board')
        super(NewTopicForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        topic = super(NewTopicForm, self).save(commit=False)
        if commit:
            topic.board = self.board
            topic.starter = self.user
            topic.save()

            Post.objects.create(
                message=self.cleaned_data.get('message'),
                topic=topic,
                created_by=self.user
            )
        return topic


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['message']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.topic = kwargs.pop('topic')
        super(PostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True, **kwargs):
        post = super(PostForm, self).save(commit=False)
        if commit:
            post.topic = self.topic
            post.created_by = self.user
            post.save()

            self.topic.last_updated = timezone.now()
            self.topic.save()
        return post


class PostUpdateForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['message']
