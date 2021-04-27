from django import forms

from .models import Post, PostImage, Comment


class CreatePostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['content']


class ImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image', ]


ImageFormSet = forms.modelformset_factory(
    PostImage,
    form=ImageForm,
    extra=3,
    max_num=5,
    can_delete=True
)


class UpdatePostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content', ]


class SearchForm(forms.Form):
    query = forms.CharField()
