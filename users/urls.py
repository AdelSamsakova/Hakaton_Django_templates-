from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import LogoutView


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
]
