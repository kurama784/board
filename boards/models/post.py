from datetime import datetime, timedelta, date
from datetime import time as dtime
import os
from random import random
import time
import re
import hashlib

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.db import models, transaction
from django.utils import timezone
from markupfield.fields import MarkupField

from neboard import settings
from boards import thumbs

from sorl.thumbnail.main import DjangoThumbnail


APP_LABEL_BOARDS = 'boards'

CACHE_KEY_PPD = 'ppd'
CACHE_KEY_POST_URL = 'post_url'
CACHE_KEY_OPENING_POST = 'opening_post_id'

POSTS_PER_DAY_RANGE = range(7)

BAN_REASON_AUTO = 'Auto'

IMAGE_THUMB_SIZE = (200, 150)

TITLE_MAX_LENGTH = 200

DEFAULT_MARKUP_TYPE = 'markdown'

NO_PARENT = -1
NO_IP = '0.0.0.0'
UNKNOWN_UA = ''
ALL_PAGES = -1
IMAGES_DIRECTORY = 'images/'
FILE_EXTENSION_DELIMITER = '.'

SETTING_MODERATE = "moderate"

REGEX_REPLY = re.compile('>>(\d+)')


class PostManager(models.Manager):

    def create_post(self, title, text, image=None, thread=None,
                    ip=NO_IP, tags=None, user=None):
        """
        Creates new post
        """

        posting_time = timezone.now()
        if not thread:
            thread = Thread.objects.create(bump_time=posting_time,
                                           last_edit_time=posting_time)
            new_thread = True
        else:
            thread.bump()
            thread.last_edit_time = posting_time
            thread.save()
            new_thread = False

        post = self.create(title=title,
                           text=text,
                           pub_time=posting_time,
                           thread_new=thread,
                           image=image,
                           poster_ip=ip,
                           poster_user_agent=UNKNOWN_UA,  # TODO Get UA at
                           # last!
                           last_edit_time=posting_time,
                           user=user)

        thread.replies.add(post)
        if tags:
            linked_tags = []
            for tag in tags:
                tag_linked_tags = tag.get_linked_tags()
                if len(tag_linked_tags) > 0:
                    linked_tags.extend(tag_linked_tags)

            tags.extend(linked_tags)
            map(thread.add_tag, tags)

        if new_thread:
            self._delete_old_threads()
        self.connect_replies(post)

        return post

    def delete_post(self, post):
        """
        Deletes post and update or delete its thread
        """

        thread = post.get_thread()

        if post.is_opening():
            thread.delete_with_posts()
        else:
            thread.last_edit_time = timezone.now()
            thread.save()

            post.delete()

    def delete_posts_by_ip(self, ip):
        """
        Deletes all posts of the author with same IP
        """

        posts = self.filter(poster_ip=ip)
        map(self.delete_post, posts)

    # TODO Move this method to thread manager
    def _delete_old_threads(self):
        """
        Preserves maximum thread count. If there are too many threads,
        archive the old ones.
        """

        threads = Thread.objects.filter(archived=False).order_by('-bump_time')
        thread_count = threads.count()

        if thread_count > settings.MAX_THREAD_COUNT:
            num_threads_to_delete = thread_count - settings.MAX_THREAD_COUNT
            old_threads = threads[thread_count - num_threads_to_delete:]

            for thread in old_threads:
                thread.archived = True
                thread.last_edit_time = timezone.now()
                thread.save()

    def connect_replies(self, post):
        """
        Connects replies to a post to show them as a reflink map
        """

        for reply_number in re.finditer(REGEX_REPLY, post.text.raw):
            post_id = reply_number.group(1)
            ref_post = self.filter(id=post_id)
            if ref_post.count() > 0:
                referenced_post = ref_post[0]
                referenced_post.referenced_posts.add(post)
                referenced_post.last_edit_time = post.pub_time
                referenced_post.save()

                referenced_thread = referenced_post.get_thread()
                referenced_thread.last_edit_time = post.pub_time
                referenced_thread.save()

    def get_posts_per_day(self):
        """
        Gets average count of posts per day for the last 7 days
        """

        today = date.today()
        ppd = cache.get(CACHE_KEY_PPD + str(today))
        if ppd:
            return ppd

        posts_per_days = []
        for i in POSTS_PER_DAY_RANGE:
            day_end = today - timedelta(i + 1)
            day_start = today - timedelta(i + 2)

            day_time_start = timezone.make_aware(datetime.combine(
                day_start, dtime()), timezone.get_current_timezone())
            day_time_end = timezone.make_aware(datetime.combine(
                day_end, dtime()), timezone.get_current_timezone())

            posts_per_days.append(float(self.filter(
                pub_time__lte=day_time_end,
                pub_time__gte=day_time_start).count()))

        ppd = (sum(posts_per_day for posts_per_day in posts_per_days) /
               len(posts_per_days))
        cache.set(CACHE_KEY_PPD + str(today), ppd)
        return ppd


class Post(models.Model):
    """A post is a message."""

    objects = PostManager()

    class Meta:
        app_label = APP_LABEL_BOARDS

    # TODO Save original file name to some field
    def _update_image_filename(self, filename):
        """
        Gets unique image filename
        """

        path = IMAGES_DIRECTORY
        new_name = str(int(time.mktime(time.gmtime())))
        new_name += str(int(random() * 1000))
        new_name += FILE_EXTENSION_DELIMITER
        new_name += filename.split(FILE_EXTENSION_DELIMITER)[-1:][0]

        return os.path.join(path, new_name)

    title = models.CharField(max_length=TITLE_MAX_LENGTH)
    pub_time = models.DateTimeField()
    text = MarkupField(default_markup_type=DEFAULT_MARKUP_TYPE,
                       escape_html=False)

    image_width = models.IntegerField(default=0)
    image_height = models.IntegerField(default=0)

    image_pre_width = models.IntegerField(default=0)
    image_pre_height = models.IntegerField(default=0)

    image = thumbs.ImageWithThumbsField(upload_to=_update_image_filename,
                                        blank=True, sizes=(IMAGE_THUMB_SIZE,),
                                        width_field='image_width',
                                        height_field='image_height',
                                        preview_width_field='image_pre_width',
                                        preview_height_field='image_pre_height')
    image_hash = models.CharField(max_length=36)

    poster_ip = models.GenericIPAddressField()
    poster_user_agent = models.TextField()

    thread = models.ForeignKey('Post', null=True, default=None)
    thread_new = models.ForeignKey('Thread', null=True, default=None)
    last_edit_time = models.DateTimeField()
    user = models.ForeignKey('User', null=True, default=None)

    referenced_posts = models.ManyToManyField('Post', symmetrical=False,
                                              null=True,
                                              blank=True, related_name='rfp+')

    def __unicode__(self):
        return '#' + str(self.id) + ' ' + self.title + ' (' + \
               self.text.raw[:50] + ')'


    def slide_thumbnail(self, width=100, height=100):
	if self.image:
		thumb = DjangoThumbnail(self.image, (width, height))
		return '<img src="%s" />' % thumb.absolute_url
	return None
    slide_thumbnail.allow_tags = True

    

   
    def get_title(self):
        """
        Gets original post title or part of its text.
        """

        title = self.title
        if not title:
            title = self.text.rendered

        return title

    def get_sorted_referenced_posts(self):
        return self.referenced_posts.order_by('id')

    def is_referenced(self):
        return self.referenced_posts.exists()

    def is_opening(self):
        """
        Checks if this is an opening post or just a reply.
        """

        return self.get_thread().get_opening_post_id() == self.id

    def save(self, *args, **kwargs):
        """
        Saves the model and computes the image hash for deduplication purposes.
        """

        if not self.pk and self.image:
            md5 = hashlib.md5()
            for chunk in self.image.chunks():
                md5.update(chunk)
            self.image_hash = md5.hexdigest()
        super(Post, self).save(*args, **kwargs)

    @transaction.atomic
    def add_tag(self, tag):
        edit_time = timezone.now()

        thread = self.get_thread()
        thread.add_tag(tag)
        self.last_edit_time = edit_time
        self.save()

        thread.last_edit_time = edit_time
        thread.save()

    @transaction.atomic
    def remove_tag(self, tag):
        edit_time = timezone.now()

        thread = self.get_thread()
        thread.remove_tag(tag)
        self.last_edit_time = edit_time
        self.save()

        thread.last_edit_time = edit_time
        thread.save()

    def get_url(self, thread=None):
        """
        Gets full url to the post.
        """

        cache_key = CACHE_KEY_POST_URL + str(self.id)
        link = cache.get(cache_key)

        if not link:
            if not thread:
                thread = self.get_thread()

            opening_id = thread.get_opening_post_id()

            if self.id != opening_id:
                link = reverse('thread', kwargs={
                    'post_id': opening_id}) + '#' + str(self.id)
            else:
                link = reverse('thread', kwargs={'post_id': self.id})

            cache.set(cache_key, link)

        return link

    def get_thread(self):
        """
        Gets post's thread.
        """

        return self.thread_new

class Thread(models.Model):

    class Meta:
        app_label = APP_LABEL_BOARDS

    tags = models.ManyToManyField('Tag')
    bump_time = models.DateTimeField()
    last_edit_time = models.DateTimeField()
    replies = models.ManyToManyField('Post', symmetrical=False, null=True,
                                     blank=True, related_name='tre+')
    archived = models.BooleanField(default=False)

    def get_tags(self):
        """
        Gets a sorted tag list.
        """

        return self.tags.order_by('name')

    def bump(self):
        """
        Bumps (moves to up) thread if possible.
        """

        if self.can_bump():
            self.bump_time = timezone.now()

    def get_reply_count(self):
        return self.replies.count()

    def get_images_count(self):
        return self.replies.filter(image_width__gt=0).count()

    def can_bump(self):
        """
        Checks if the thread can be bumped by replying to it.
        """

        if self.archived:
            return False

        post_count = self.get_reply_count()

        return post_count < settings.MAX_POSTS_PER_THREAD

    def delete_with_posts(self):
        """
        Completely deletes thread and all its posts
        """

        if self.replies.exists():
            self.replies.all().delete()

        self.delete()

    def get_last_replies(self):
        """
        Gets several last replies, not including opening post
        """

        if settings.LAST_REPLIES_COUNT > 0:
            reply_count = self.get_reply_count()

            if reply_count > 0:
                reply_count_to_show = min(settings.LAST_REPLIES_COUNT,
                                          reply_count - 1)
                last_replies = self.replies.order_by(
                    'pub_time')[reply_count - reply_count_to_show:]

                return last_replies

    def get_skipped_replies_count(self):
        """
        Gets number of posts between opening post and last replies.
        """

        last_replies = self.get_last_replies()
        return self.get_reply_count() - len(last_replies) - 1

    def get_replies(self):
        """
        Gets sorted thread posts
        """

        return self.replies.all().order_by('pub_time')

    def add_tag(self, tag):
        """
        Connects thread to a tag and tag to a thread
        """

        self.tags.add(tag)
        tag.threads.add(self)

    def remove_tag(self, tag):
        self.tags.remove(tag)
        tag.threads.remove(self)

    def get_opening_post(self):
        """
        Gets the first post of the thread
        """

        opening_post = self.get_replies()[0]

        return opening_post

    def get_opening_post_id(self):
        """
        Gets ID of the first thread post.
        """

        cache_key = CACHE_KEY_OPENING_POST + str(self.id)
        opening_post_id = cache.get(cache_key)
        if not opening_post_id:
            opening_post_id = self.get_opening_post().id
            cache.set(cache_key, opening_post_id)

        return opening_post_id

    def __unicode__(self):
        return str(self.id)

    def get_pub_time(self):
        """
        Gets opening post's pub time because thread does not have its own one.
        """

        return self.get_opening_post().pub_time
