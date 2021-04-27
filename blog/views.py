import sys
from datetime import datetime, timedelta

import django_filters
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView

from blog.forms import CreatePostForm, ImageFormSet, CommentForm, SearchForm, UpdatePostForm
from blog.models import Post, PostImage, Comment


def check_users(post_user, logged_user):
    return post_user == logged_user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 4


class PostDetailsView(LoginRequiredMixin, DetailView):
    queryset = Post.objects.all()
    template_name = 'blog/post_detail2.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = CommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return redirect(new_comment.get_absolute_url())


class CreatePostView(LoginRequiredMixin, CreateView):
    def get(self, request):
        form = CreatePostForm(instance=self.request.user)
        images_form = ImageFormSet(queryset=PostImage.objects.none())
        return render(request, 'blog/create.html', locals())

    def post(self, request):
        form = CreatePostForm(request.POST)
        form.instance.author = self.request.user
        images_form = ImageFormSet(request.POST,
                                   request.FILES,
                                   queryset=PostImage.objects.none())
        if form.is_valid() and images_form.is_valid():
            posts = form.save()
            for i_form in images_form.cleaned_data:
                image = i_form.get('image')
                if image is not None:
                    pic = PostImage(post=posts, image=image)
                    pic.save()
            return redirect(posts.get_absolute_url())
        print(form.errors, images_form.errors)


class PostEditView(View):
    def get(self, request, pk):
        posts = get_object_or_404(Post, pk=pk)
        form = UpdatePostForm(instance=posts)
        images_form = ImageFormSet(queryset=posts.images.all())
        return render(request, 'blog/edit.html', locals())

    def post(self, request, pk):
        posts = get_object_or_404(Post, pk=pk)
        form = UpdatePostForm(instance=posts, data=request.POST)
        form.instance.author = self.request.user
        images_form = ImageFormSet(request.POST,
                                   request.FILES,
                                   queryset=posts.images.all())
        if form.is_valid() and images_form.is_valid():
            posts = form.save()
            for i_form in images_form.cleaned_data:
                image = i_form.get('image')
                if image is not None and not PostImage.objects.filter(post=posts, image=image).exists():
                    pic = PostImage(post=posts, image=image)
                    pic.save()
            for i_form in images_form.deleted_forms:
                image = i_form.cleaned_data.get('id')
                if image is not None:
                    image.delete()
            return redirect(posts.get_absolute_url())
        print(form.errors, images_form.errors)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        return check_users(self.get_object().author, self.request.user)


class SearchResultsView(View):
    def get(self, request):
        search_param = request.GET.get('query', 'search')
        results = Post.objects.filter(Q(content__icontains=search_param))
        return render(request, 'blog/search_results.html', locals())


# def beats_by_user(request, author):
#     beats = Post.objects.get(author=author)
#     return render(request, 'blog/post_filter.html', {'beats': beats})


class PostFilter(django_filters.FilterSet):
    author = django_filters.CharFilter('author')

    class Meta:
        model = Post
        fields = ['author', ]

