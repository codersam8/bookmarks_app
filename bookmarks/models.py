from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import models
from django.template.loader import get_template


class Link(models.Model):
    url = models.URLField(unique=True)

    def __str__(self):
        return self.url


class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.ForeignKey(Link, on_delete=models.CASCADE)

    def __str__(self):
        return '''title: {0}, user: {1}, link: {2}'''.format(self.title,
                                                             self.user,
                                                             self.link)


class SharedBookmark(models.Model):
    bookmark = models.OneToOneField(Bookmark,
                                    on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    votes = models.IntegerField(default=1)
    users_voted = models.ManyToManyField(User)


class Tag(models.Model):
    name = models.CharField(max_length=64,
                            unique=True)
    bookmarks = models.ManyToManyField(Bookmark)

    def __str__(self):
        return self.name


class Friendship(models.Model):
    from_friend = models.ForeignKey(
        User, related_name='friend_set',
        on_delete=models.CASCADE)
    to_friend = models.ForeignKey(
        User, related_name='to_friend_set',
        on_delete=models.CASCADE)

    def __str__(self):
        return '%s, %s' % (
            self.from_friend.username,
            self.to_friend.username)

    class Meta:
        unique_together = (('to_friend', 'from_friend'), )


class Invitation(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    code = models.CharField(max_length=20)
    sender = models.ForeignKey(User,
                               on_delete=models.CASCADE)

    def send(self):
        subject = 'Invitation to join Django Bookmarks'
        link = 'http://%s/bookmarks/friend/accept/%s/' % (
            settings.SITE_HOST,
            self.code
        )
        template = get_template('bookmarks/invitation_email.txt')
        context = {
            'name': self.name,
            'link': link,
            'sender': self.sender.username,
        }
        message = template.render(context)
        resp = send_mail(
            subject, message,
            settings.DEFAULT_FROM_EMAIL, [self.email]
        )

    def __str__(self):
        return '%s, %s' % (self.sender.username, self.email)
