from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render

from .models import Bookmark, Link, Tag
from .forms import BookmarkSaveForm


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


@login_required
def bookmark_save_page(request):
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        if form.is_valid():
            link, is_created = Link.objects.get_or_create(
                url=form.cleaned_data['url']
            )
            bookmark, is_b_created = Bookmark.objects.get_or_create(
                user=request.user,
                link=link)
            bookmark.title = form.cleaned_data['title']
            if not is_b_created:
                bookmark.tag_set.clear()
            tag_names = form.cleaned_data['tags'].split()
            for tag_name in tag_names:
                tag, dummy = Tag.objects.get_or_create(name=tag_name)
                bookmark.tag_set.add(tag)
            bookmark.save()
            return HttpResponseRedirect('/bookmarks')
    else:
        form = BookmarkSaveForm()
        context = {
            'form': form}
        return render(request, 'bookmarks/bookmark_save.html', context)
