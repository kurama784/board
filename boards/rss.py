from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from boards.models import Post, Tag, Thread
from neboard import settings

__author__ = 'neko259'


# TODO Make tests for all of these
class AllThreadsFeed(Feed):

    title = settings.SITE_NAME + ' - All threads'
    link = '/'
    description_template = 'boards/rss/post.html'

    def items(self):
        return Thread.objects.filter(archived=False).order_by('-id')

    def item_title(self, item):
        return item.get_opening_post().title

    def item_link(self, item):
        return reverse('thread', args={item.get_opening_post_id()})

    def item_pubdate(self, item):
        return item.get_pub_time()


class TagThreadsFeed(Feed):

    link = '/'
    description_template = 'boards/rss/post.html'

    def items(self, obj):
        return obj.threads.filter(archived=False).order_by('-id')

    def get_object(self, request, tag_name):
        return get_object_or_404(Tag, name=tag_name)

    def item_title(self, item):
        return item.get_opening_post().title

    def item_link(self, item):
        return reverse('thread', args={item.get_opening_post_id()})

    def item_pubdate(self, item):
        return item.get_pub_time()

    def title(self, obj):
        return obj.name


class ThreadPostsFeed(Feed):

    link = '/'
    description_template = 'boards/rss/post.html'

    def items(self, obj):
        return obj.get_thread().get_replies()

    def get_object(self, request, post_id):
        return get_object_or_404(Post, id=post_id)

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        if not item.is_opening():
            return reverse('thread', args={
                item.get_thread().get_opening_post_id()
            }) + "#" + str(item.id)
        else:
            return reverse('thread', args={item.id})

    def item_pubdate(self, item):
        return item.pub_time

    def title(self, obj):
        return obj.title
