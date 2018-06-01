from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import render


def main_page(request):
    return render(request, 'bookmarks/main_page.html', {})


def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except Exception:
        raise Http404('Requested user not found')
    bookmarks = user.bookmark_set.all()
    context = {
        'username': username,
        'bookmarks': bookmarks
    }
    return render(request, 'bookmarks/user_page.html', context)
