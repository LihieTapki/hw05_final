from django import forms

from posts.models import Comment, Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        group = forms.ModelChoiceField(
            queryset=Group.objects.all(),
            widget=forms.Select(
                attrs={
                    'cols': '40',
                    'rows': '10',
                    'class': 'form-control',
                },
            ),
        )
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'cols': '40',
                    'rows': '10',
                    'class': 'form-control',
                },
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
