from django.db import models
from django.db.models import Count
from boards import settings
from boards.models import Post
from django.core.cache import cache

__author__ = 'neko259'

RANK_ADMIN = 0
RANK_MODERATOR = 10
RANK_USER = 100

BAN_REASON_AUTO = 'Auto'
BAN_REASON_MAX_LENGTH = 200


class User(models.Model):

    class Meta:
        app_label = 'boards'

    user_id = models.CharField(max_length=50)
    rank = models.IntegerField()

    registration_time = models.DateTimeField()

    fav_tags = models.ManyToManyField('Tag', null=True, blank=True)
    fav_threads = models.ManyToManyField(Post, related_name='+', null=True,
                                         blank=True)

    def save_setting(self, name, value):
        setting, created = Setting.objects.get_or_create(name=name, user=self)
        setting.value = str(value)
        setting.save()

        return setting

    def get_setting(self, name):
        if Setting.objects.filter(name=name, user=self).exists():
            setting = Setting.objects.get(name=name, user=self)
            setting_value = setting.value
        else:
            setting_value = None

        return setting_value

    def is_moderator(self):
        return RANK_MODERATOR >= self.rank

    def get_sorted_fav_tags(self):
        cache_key = self._get_tag_cache_key()
        fav_tags = cache.get(cache_key)
        if fav_tags:
            return fav_tags

        tags = self.fav_tags.annotate(Count('threads')) \
            .filter(threads__count__gt=0).order_by('name')

        if tags:
            cache.set(cache_key, tags)

        return tags

    def get_post_count(self):
        return Post.objects.filter(user=self).count()

    def __unicode__(self):
        return self.user_id + '(' + str(self.rank) + ')'

    def get_last_access_time(self):
        """
        Gets user's last post time.
        """

        posts = Post.objects.filter(user=self)
        if posts.exists() > 0:
            return posts.latest('pub_time').pub_time

    def add_tag(self, tag):
        self.fav_tags.add(tag)
        cache.delete(self._get_tag_cache_key())

    def remove_tag(self, tag):
        self.fav_tags.remove(tag)
        cache.delete(self._get_tag_cache_key())

    def _get_tag_cache_key(self):
        return self.user_id + '_tags'


class Setting(models.Model):

    class Meta:
        app_label = 'boards'

    name = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    user = models.ForeignKey(User)


class Ban(models.Model):

    class Meta:
        app_label = 'boards'

    ip = models.GenericIPAddressField()
    reason = models.CharField(default=BAN_REASON_AUTO,
                              max_length=BAN_REASON_MAX_LENGTH)
    can_read = models.BooleanField(default=True)

    def __unicode__(self):
        return self.ip
