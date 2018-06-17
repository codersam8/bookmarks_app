from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import RegistrationForm

from bookmarks.models import Friendship, Invitation

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/bookmarks')


def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            if 'invitation' in request.session:
                # Retrieve the invitation object.
                invitation = \
                    Invitation.objects.get(id=request.session['invitation'])
                # Create friendship from user to sender.
                friendship = Friendship(
                    from_friend=user,
                    to_friend=invitation.sender
                )
                friendship.save()
                # Create friendship from sender to user.
                friendship = Friendship(
                    from_friend=invitation.sender,
                    to_friend=user
                )
                friendship.save()
                # Delete the invitation from the database and session.
                invitation.delete()
                del request.session['invitation']
            return HttpResponseRedirect('/register/success/')
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, 'registration/register.html', context)
