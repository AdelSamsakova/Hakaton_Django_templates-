from django.urls import path

from blog.views import PostListView, PostDetailsView, CreatePostView, PostDeleteView, PostEditView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('posts/create/', CreatePostView.as_view(), name='create-post'),
    path('posts/<int:pk>', PostDetailsView.as_view(), name='post-details'),
    path('posts/delete/<int:pk>', PostDeleteView.as_view(), name='post-delete'),
    path('posts/edit/<int:pk>', PostEditView.as_view(), name='post-edit'),
]
