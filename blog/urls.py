from django.urls import path
from django.views.defaults import permission_denied

from blog import views
from blog.views import PostListView, PostDetailsView, CreatePostView, PostDeleteView, PostEditView, SearchResultsView

urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('posts/create/', CreatePostView.as_view(), name='create-post'),
    path('posts/search/', SearchResultsView.as_view(), name='search-results'),
    path('posts/<int:pk>', PostDetailsView.as_view(), name='post-details'),
    path('posts/delete/<int:pk>', PostDeleteView.as_view(), name='post-delete'),
    path('posts/edit/<int:pk>', PostEditView.as_view(), name='post-edit'),
    path('posts/filter<int:types>', views.post_filter, name='post-filter'),
]
