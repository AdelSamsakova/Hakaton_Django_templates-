from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, user_logged_out, logout
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import CreateView

from .forms import LoginForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required

from .models import Profile


@login_required
def dashboard(request):
    return render(request, 'registration/dashboard.html', {'section': 'dashboard'})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username=cd['username'],
                                password=cd['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponse('Authenticated successfully')
            else:
                return HttpResponse('Disabled account')
        else:
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return render(request, 'blog/index.html')


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Создаем нового пользователя, но пока не сохраняем в базу данных.
            new_user = user_form.save(commit=False)
            # Задаем пользователю зашифрованный пароль.
            new_user.set_password(user_form.cleaned_data['password'])
            # Сохраняем пользователя в базе данных.
            new_user.save()
            return render(request, 'registration/register_done.html',{'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})

