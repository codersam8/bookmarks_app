from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import Bookmark, Link, Tag
from .forms import BookmarkSaveForm


def main_page(request):
    return render(request, 'bookmarks/main_page.html', {})


def tag_cloud_page(request):
    MAX_WEIGHT = 5
    tags = Tag.objects.order_by('name')
    min_count = max_count = tags[0].bookmarks.count()
    for tag in tags:
        tag.count = tag.bookmarks.count()
        if tag.count < min_count:
            min_count = tag.count
        if max_count < tag.count:
            max_count = tag.count

    tag_range = float(max_count - min_count)
    if tag_range == 0.0:
        tag_range = 1.0
    for tag in tags:
        tag.weight = int(
            MAX_WEIGHT * (tag.count - min_count) / tag_range)
    context = {
        'tags': tags
    }
    return render(request, 'bookmarks/tag_cloud_page.html', context)


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
