from boards.models import Thread, Post
from django.db import models
from django.db.models import Count, Sum

__author__ = 'neko259'

MAX_TAG_FONT = 1
MIN_TAG_FONT = 0.2

TAG_POPULARITY_MULTIPLIER = 20

ARCHIVE_POPULARITY_MODIFIER = 0.5


class TagManager(models.Manager):

    def get_not_empty_tags(self):
        """
        Gets tags that have non-archived threads.
        """

        tags = self.annotate(Count('threads')) \
            .filter(threads__count__gt=0).filter(threads__archived=False) \
            .order_by('name')

        return tags


class Tag(models.Model):
    """
    A tag is a text node assigned to the thread. The tag serves as a board
    section. There can be multiple tags for each thread
    """

    objects = TagManager()

    class Meta:
        app_label = 'boards'

    name = models.CharField(max_length=100, db_index=True)
    threads = models.ManyToManyField(Thread, null=True,
                                     blank=True, related_name='tag+')
    linked = models.ForeignKey('Tag', null=True, blank=True)

    def __unicode__(self):
        return self.name

    def is_empty(self):
        """
        Checks if the tag has some threads.
        """

        return self.get_thread_count() == 0

    def get_thread_count(self):
        return self.threads.count()

    def get_popularity(self):
        """
        Gets tag's popularity value as a percentage of overall board post
        count.
        """

        all_post_count = Post.objects.count()

        tag_reply_count = 0.0

        tag_reply_count += self.get_post_count()
        tag_reply_count +=\
            self.get_post_count(archived=True) * ARCHIVE_POPULARITY_MODIFIER

        popularity = tag_reply_count / all_post_count

        return popularity

    def get_linked_tags(self):
        """
        Gets tags linked to the current one.
        """

        tag_list = []
        self.get_linked_tags_list(tag_list)

        return tag_list

    def get_linked_tags_list(self, tag_list=[]):
        """
        Returns the list of tags linked to current. The list can be got
        through returned value or tag_list parameter
        """

        linked_tag = self.linked

        if linked_tag and not (linked_tag in tag_list):
            tag_list.append(linked_tag)

            linked_tag.get_linked_tags_list(tag_list)

    def get_font_value(self):
        """
        Gets tag font value to differ most popular tags in the list
        """

        popularity = self.get_popularity()

        font_value = popularity * Tag.objects.get_not_empty_tags().count()
        font_value = max(font_value, MIN_TAG_FONT)
        font_value = min(font_value, MAX_TAG_FONT)

        return str(font_value)

    def get_post_count(self, archived=False):
        """
        Gets posts count for the tag's threads.
        """

        posts_count = 0

        threads = self.threads.filter(archived=archived)
        if threads.exists():
            posts_count = threads.annotate(posts_count=Count('replies')).aggregate(
                posts_sum=Sum('posts_count'))['posts_sum']

        if not posts_count:
            posts_count = 0

        return posts_count
