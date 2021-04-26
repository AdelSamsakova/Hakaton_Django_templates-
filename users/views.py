from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, user_logged_out, logout
from .forms import LoginForm,UserRegistrationForm
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    return render(request,'registration/dashboard.html',{'section': 'dashboard'})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,
                                username =cd['username'],
                                password = cd['password'])
        if user is not None:
            if user.is_active:
                login(request,user)
                return HttpResponse ('Authenticated successfully')
            else:
                return HttpResponse ('Disabled account')
        else:
            return HttpResponse('Invalid login')
    else:
        form = LoginForm()
        return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return render(request, 'blog/post_list.html')

# def logout(request):
#     """
#     Removes the authenticated user's ID from the request and flushes their
#     session data.
#     """
#     # Dispatch the signal before the user is logged out so the receivers have a
#     # chance to find out *who* logged out.
#     user = getattr(request, 'user', None)
#     if hasattr(user, 'is_authenticated') and not user.is_authenticated():
#         user = None
#     user_logged_out.send(sender=user.__class__, request=request, user=user)
#
#     request.session.flush()
#     if hasattr(request, 'user'):
#         from django.contrib.auth.models import AnonymousUser
#         request.user = AnonymousUser()
#         return render(request, 'blog/post_list.html', )


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
            return render(request,'registration/register_done.html',{'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,'registration/register.html',{'user_form': user_form})
