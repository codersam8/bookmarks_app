from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template import loader


def main_page(request):
    template = loader.get_template('bookmarks/main_page.html')

    return HttpResponse(template.render({}, request))


def user_page(request, username):
    try:
        user = User.objects.get(username=username)
    except Exception:
        raise Http404('Requested user not found')
    bookmarks = user.bookmark_set.all()
    template = loader.get_template('bookmarks/user_page.html')
    context = {
        'username': username,
        'bookmarks': bookmarks
    }
    return HttpResponse(template.render(context, request))
