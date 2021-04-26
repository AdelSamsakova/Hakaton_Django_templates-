import sys

import django_filters
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView

from blog.forms import CreatePostForm, ImageFormSet, UpdatePostForm, CommentForm
from blog.models import Post, PostImage, Comment
from users.models import Follow


# class UserPostListView(ListView):
#     model = Post
#     template_name = 'blog/user_posts.html'
#     context_object_name = 'posts'
#     paginate_by = 4
#
#     def visible_user(self):
#         return get_object_or_404(User, username=self.kwargs.get('username'))
#
#     def get_context_data(self, **kwargs):
#         visible_user = self.visible_user()
#         logged_user = self.request.user
#         print(logged_user.username == '', file=sys.stderr)
#
#         if logged_user.username == '' or logged_user is None:
#             can_follow = False
#         else:
#             can_follow = (Follow.objects.filter(user=logged_user,
#                                                 follow_user=visible_user).count() == 0)
#         data = super().get_context_data(**kwargs)
#
#         data['user_profile'] = visible_user
#         data['can_follow'] = can_follow
#         return data
#
#     def get_queryset(self):
#         user = self.visible_user()
#         return Post.objects.filter(author=user).order_by('-date_posted')
#
#     def post(self, request, *args, **kwargs):
#         if request.user.id is not None:
#             follows_between = Follow.objects.filter(user=request.user,
#                                                     follow_user=self.visible_user())
#
#             if 'follow' in request.POST:
#                     new_relation = Follow(user=request.user, follow_user=self.visible_user())
#                     if follows_between.count() == 0:
#                         new_relation.save()
#             elif 'unfollow' in request.POST:
#                     if follows_between.count() > 0:
#                         follows_between.delete()
#
#         return self.get(self, request, *args, **kwargs)


class IsAdminCheckMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 4


class PostDetailsView(DetailView):
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

        # return self.get(self, request, *args, **kwargs)
        return redirect(new_comment.get_absolute_url())


class CreatePostView(View):
    def get(self, request):
        form = CreatePostForm()
        images_form = ImageFormSet(queryset=PostImage.objects.none())
        return render(request, 'blog/create.html', locals())

    def post(self, request):
        form = CreatePostForm(request.POST)
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


class PostDeleteView(DeleteView):
    model = Post
    template_name = 'blog/delete.html'
    success_url = reverse_lazy('post-list')


# class PostFilter(django_filters.FilterSet):
#     start_date = django_filters.DateTimeFilter('date_posted', 'gte')
#     end_date = django_filters.DateTimeFilter('date_posted', 'lte')
#
#     class Meta:
#         model = Post
#         fields = ['start_date', 'end_date']


class SearchResultsView(View):
    def get(self, request):
        search_param = request.GET.get('query')
        results = Post.objects.filter(Q(content__icontains=search_param))
                                      # | Q(author=search_param))
        return render(request, 'blog/search_results.html', locals())



