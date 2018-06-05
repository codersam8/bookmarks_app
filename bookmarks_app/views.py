from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import RegistrationForm


def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/bookmarks')


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'])
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)
