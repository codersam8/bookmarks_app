from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import Bookmark, Link, Tag
from .forms import BookmarkSaveForm


def main_page(request):
    return render(request, 'bookmarks/main_page.html', {})


def tag_page(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    bookmarks = tag.bookmarks.order_by('-id')
    context = {
        'bookmarks': bookmarks,
        'tag_name': tag_name,
        'show_tags': True,
        'show_user': True
    }
    return render(request, 'bookmarks/tag_page.html', context)


def user_page(request, username):
    user = get_object_or_404(User, username=username)
    bookmarks = user.bookmark_set.order_by('-id')
    context = {
        'username': username,
        'bookmarks': bookmarks,
        'show_tags': True
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
            return HttpResponseRedirect('/bookmarks/user/%s/' % request.user.username)
    else:
        form = BookmarkSaveForm()
        context = {
            'form': form}
        return render(request, 'bookmarks/bookmark_save.html', context)
