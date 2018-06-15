import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from .models import Bookmark, Friendship, Link, SharedBookmark, Tag, Invitation
from .forms import BookmarkSaveForm, SearchForm, FriendInviteForm


def ajax_tag_autocomplete(request):
    if 'term' in request.GET:
        tags = \
               Tag.objects.filter(name__istartswith=request.GET['term'])[:10]
        all_tags = [tag.name for tag in tags]
        return HttpResponse(json.dumps(all_tags))


def main_page(request):
    shared_bookmarks = SharedBookmark.objects.order_by(
        '-date')
    context = {
        'shared_bookmarks': shared_bookmarks
    }
    return render(request, 'bookmarks/main_page.html', context)


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


def search_page(request):
    form = SearchForm()
    bookmarks = []
    show_results = False
    if 'query' in request.GET:
        show_results = True
        query = request.GET['query'].strip()
        if query:
            form = SearchForm({'query': query})
            bookmarks = Bookmark.objects.filter(title__icontains=query)[:10]
    context = {
        'form': form,
        'bookmarks': bookmarks,
        'show_results': show_results,
        'show_tags': True,
        'show_user': True
    }
    if 'ajax' in request.GET:
        return render(request, 'bookmarks/bookmark_list.html', context)
    else:
        return render(request, 'bookmarks/search.html', context)


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
    is_friend = Friendship.objects.filter(
        from_friend=request.user,
        to_friend=user)
    bookmarks = user.bookmark_set.order_by('-id')
    context = {
        'username': username,
        'bookmarks': bookmarks,
        'is_friend': is_friend,
        'show_tags': True,
        'show_edit': username == request.user.username
    }
    return render(request, 'bookmarks/user_page.html', context)


@login_required
def bookmark_save_page(request):
    ajax = 'ajax' in request.GET
    if request.method == 'POST':
        form = BookmarkSaveForm(request.POST)
        post_data = (request.read())
        if form.is_valid():
            bookmark = _bookmark_save(request, form)
            # ajax = post_data['ajax']
            if ajax:
                context = {
                    'bookmarks': [bookmark],
                    'show_edit': True,
                    'show_tags': True
                }
                return render(request,
                              'bookmarks/bookmark_list.html',
                              context)
            else:
                return HttpResponseRedirect(
                    '/bookmarks/user/%s' % request.user.username)
        else:
            if ajax:
                return HttpResponse('failure')
    elif 'url' in request.GET:
        url = request.GET['url']
        title = ''
        tags = ''
        try:
            link = Link.objects.get(url=url)
            bookmark = Bookmark.objects.get(
                link=link,
                user=request.user)
            title = bookmark.title
            tags = ' '.join(
                tag.name for tag in bookmark.tag_set.all())
        except ObjectDoesNotExist:
            pass
        form = BookmarkSaveForm({
            'url': url,
            'title': title,
            'tags': tags})
    else:
        form = BookmarkSaveForm()
    context = {
        'form': form}
    if ajax:
        return render(request, 'bookmarks/bookmark_save_form.html', context)
    else:
        return render(request, 'bookmarks/bookmark_save.html', context)


def _bookmark_save(request, form):
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
    if form.cleaned_data['share']:
        shared_bookmark, created = SharedBookmark.objects.get_or_create(
            bookmark=bookmark)
        if created:
            shared_bookmark.users_voted.add(request.user)
            shared_bookmark.save()
    bookmark.save()
    return bookmark


@login_required
def bookmark_vote_page(request):
    if 'id' in request.GET:
        try:
            id = request.GET['id']
            shared_bookmark = SharedBookmark.objects.get(id=id)
            user_voted = shared_bookmark.users_voted.filter(
                username=request.user.username)
            if not user_voted:
                shared_bookmark.votes += 1
                shared_bookmark.users_voted.add(request.user)
                shared_bookmark.save()
        except:
            raise Http404('Bookmark not found.')
    if 'HTTP_REFERER' in request.META:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseRedirect('bookmarks/')


def popular_page(request):
    today = datetime.today()
    yesterday = today - timedelta(1)
    shared_bookmarks = SharedBookmark.objects.filter(
        date__gt=yesterday)
    shared_bookmarks = shared_bookmarks.order_by(
        '-votes')[:10]
    context = {
        'shared_bookmarks': shared_bookmarks
    }
    return render(request, 'bookmarks/popular_page.html', context)


def bookmark_page(request, bookmark_id):
    shared_bookmark = get_object_or_404(
        SharedBookmark, id=bookmark_id)
    context = {
        'shared_bookmark': shared_bookmark
    }
    return render(request, 'bookmarks/bookmark_page.html', context)


def friends_page(request, username):
    user = get_object_or_404(User, username=username)
    friends = [friendship.to_friend for friendship in user.friend_set.all()]
    friend_bookmarks = (Bookmark
                        .objects
                        .filter(user__in=friends).order_by('-id'))
    context = {
        'username': username,
        'friends': friends,
        'bookmarks': friend_bookmarks[:10],
        'show_tags': True,
        'show_user': True
    }
    return render(request, 'bookmarks/friends_page.html', context)


@login_required
def friend_add(request):
    if 'username' in request.GET:
        friend = \
                 get_object_or_404(User, username=request.GET['username'])
        friendship = Friendship(
            from_friend=request.user,
            to_friend=friend
        )
        try:
            friendship.save()
            # request.user.message_set.create(
            #     request,
            #     messages.INFO,
            #     '%s was added to your friend list.' % friend.username
            # )
        except:
            pass
            # request.user.message_set.create(
            #     request,
            #     messages.ERROR,
            #     '%s is already a friend of yours.' % friend.username
            # )
        return HttpResponseRedirect(
            '/bookmarks/friends/%s/' % request.user.username
        )
    else:
        raise Http404


@login_required
def friend_invite(request):
    if request.method == 'POST':
        form = FriendInviteForm(request.POST)
        if form.is_valid():
            invitation = Invitation(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                code=User.objects.make_random_password(20),
                sender=request.user
            )
            invitation.save()
            try:
                invitation.send()
                messages.add_message(
                    request,
                    messages.INFO,
                    'An invitation was sent to %s.' % invitation.email
                )
            except Exception as e:
                )
                messages.add_message(
                    request,
                    messages.ERROR,
                    'There was an error while sending the invitation.'
                )
            return HttpResponseRedirect('/bookmarks/friend/invite/')
    else:
        form = FriendInviteForm()
    context = {
        'form': form
    }
    return render(request, 'bookmarks/friend_invite.html', context)
