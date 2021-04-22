from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView

from blog.forms import CreatePostForm, ImageFormSet, UpdatePostForm, CommentForm
from blog.models import Post, PostImage, Comment


class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 2


class PostDetailsView(DetailView):
    queryset = Post.objects.all()
    template_name = 'blog/post_details.html'
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

        return self.get(self, request, *args, **kwargs)


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
