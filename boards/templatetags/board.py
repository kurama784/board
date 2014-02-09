from django.shortcuts import get_object_or_404
from boards.models import Post
from boards.views import thread, api
from django import template

register = template.Library()

actions = [
    {
        'name': 'google',
        'link': 'http://google.com/searchbyimage?image_url=%s',
    },
    {
        'name': 'iqdb',
        'link': 'http://iqdb.org/?url=%s',
    },
]


@register.simple_tag(name='post_url')
def post_url(*args, **kwargs):
    post_id = args[0]

    post = get_object_or_404(Post, id=post_id)

    return post.get_url()


@register.simple_tag(name='post_object_url')
def post_object_url(*args, **kwargs):
    post = args[0]

    if 'thread' in kwargs:
        post_thread = kwargs['thread']
    else:
        post_thread = None

    return post.get_url(thread=post_thread)


@register.simple_tag(name='image_actions')
def image_actions(*args, **kwargs):
    image_link = args[0]
    if len(args) > 1:
        image_link = 'http://' + args[1] + image_link # TODO https?

    result = ''

    for action in actions:
        result += '[<a href="' + action['link'] % image_link + '">' + \
                  action['name'] + '</a>]'

    return result


@register.inclusion_tag('boards/post.html', name='post_view')
def post_view(post, moderator=False, need_open_link=False, truncated=False,
              **kwargs):
    """
    Get post
    """

    if 'is_opening' in kwargs:
        is_opening = kwargs['is_opening']
    else:
        is_opening = post.is_opening()

    if 'thread' in kwargs:
        thread = kwargs['thread']
    else:
        thread = post.get_thread()

    if 'can_bump' in kwargs:
        can_bump = kwargs['can_bump']
    else:
        can_bump = thread.can_bump()

    opening_post_id = thread.get_opening_post_id()

    return {
        'post': post,
        'moderator': moderator,
        'is_opening': is_opening,
        'thread': thread,
        'bumpable': can_bump,
        'need_open_link': need_open_link,
        'truncated': truncated,
        'opening_post_id': opening_post_id,
    }
