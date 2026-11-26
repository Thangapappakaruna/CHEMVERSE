from django import forms

from config.bootstrap import BootstrapFormMixin
from reaction_builder.models import Reaction

from .models import Comment, Post


class PostForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'category', 'body', 'shared_reaction')
        widgets = {'body': forms.Textarea(attrs={'rows': 7})}
        labels = {'shared_reaction': 'Attach a reaction (optional)'}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Reaction.objects.filter(is_sample=True)
        if user is not None:
            qs = Reaction.objects.filter(user=user) | qs
        self.fields['shared_reaction'].queryset = qs.order_by('title')
        self.fields['shared_reaction'].required = False

    def clean_title(self):
        t = self.cleaned_data['title'].strip()
        if len(t) < 5:
            raise forms.ValidationError('Please write a title of at least 5 characters.')
        return t


class CommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('body',)
        widgets = {'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a helpful reply…'})}
        labels = {'body': 'Your reply'}
