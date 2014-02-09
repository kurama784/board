from datetime import datetime
import json
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import RequestContext
from django.utils import timezone
from django.core import serializers

from boards.forms import PostForm, PlainErrorList
from boards.models import Post, Thread, Tag
from boards.utils import datetime_to_epoch
from boards.views.thread import ThreadView

__author__ = 'neko259'

PARAMETER_TRUNCATED = 'truncated'
PARAMETER_TAG = 'tag'
PARAMETER_OFFSET = 'offset'
PARAMETER_DIFF_TYPE = 'type'

DIFF_TYPE_HTML = 'html'
DIFF_TYPE_JSON = 'json'

STATUS_OK = 'ok'
STATUS_ERROR = 'error'


@transaction.atomic
def api_get_threaddiff(request, thread_id, last_update_time):
    """
    Gets posts that were changed or added since time
    """

    thread = get_object_or_404(Post, id=thread_id).thread_new

    filter_time = datetime.fromtimestamp(float(last_update_time) / 1000000,
                                         timezone.get_current_timezone())

    json_data = {
        'added': [],
        'updated': [],
        'last_update': None,
    }
    added_posts = Post.objects.filter(thread_new=thread,
                                      pub_time__gt=filter_time) \
        .order_by('pub_time')
    updated_posts = Post.objects.filter(thread_new=thread,
                                        pub_time__lte=filter_time,
                                        last_edit_time__gt=filter_time)

    diff_type = DIFF_TYPE_HTML
    if PARAMETER_DIFF_TYPE in request.GET:
        diff_type = request.GET[PARAMETER_DIFF_TYPE]

    for post in added_posts:
        json_data['added'].append(_get_post_data(post.id, diff_type, request))
    for post in updated_posts:
        json_data['updated'].append(_get_post_data(post.id, diff_type, request))
    json_data['last_update'] = datetime_to_epoch(thread.last_edit_time)

    return HttpResponse(content=json.dumps(json_data))


def api_add_post(request, opening_post_id):
    """
    Adds a post and return the JSON response for it
    """

    opening_post = get_object_or_404(Post, id=opening_post_id)

    status = STATUS_OK
    errors = []

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES,
                          error_class=PlainErrorList)
        form.session = request.session

        #if form.need_to_ban:
        #    # Ban user because he is suspected to be a bot
        #    _ban_current_user(request)
        #    status = STATUS_ERROR
        if form.is_valid():
            ThreadView().new_post(request, form, opening_post,
                                  html_response=False)
        else:
            status = STATUS_ERROR
            errors = form.as_json_errors()

    response = {
        'status': status,
        'errors': errors,
    }

    return HttpResponse(content=json.dumps(response))


def get_post(request, post_id):
    """
    Gets the html of a post. Used for popups. Post can be truncated if used
    in threads list with 'truncated' get parameter.
    """

    post = get_object_or_404(Post, id=post_id)

    context = RequestContext(request)
    context['post'] = post
    if PARAMETER_TRUNCATED in request.GET:
        context[PARAMETER_TRUNCATED] = True

    return render(request, 'boards/api_post.html', context)


# TODO Test this
def api_get_threads(request, count):
    """
    Gets the JSON thread opening posts list.
    Parameters that can be used for filtering:
    tag, offset (from which thread to get results)
    """

    if PARAMETER_TAG in request.GET:
        tag_name = request.GET[PARAMETER_TAG]
        if tag_name is not None:
            tag = get_object_or_404(Tag, name=tag_name)
            threads = tag.threads.filter(archived=False)
    else: 
        threads = Thread.objects.filter(archived=False)

    if PARAMETER_OFFSET in request.GET:
        offset = request.GET[PARAMETER_OFFSET]
        offset = int(offset) if offset is not None else 0
    else:
        offset = 0

    threads = threads.order_by('-bump_time')
    threads = threads[offset:offset + int(count)]

    opening_posts = []
    for thread in threads:
        opening_post = thread.get_opening_post()

        # TODO Add tags, replies and images count
        opening_posts.append(_get_post_data(opening_post.id,
            include_last_update=True))

    return HttpResponse(content=json.dumps(opening_posts))


# TODO Test this
def api_get_tags(request):
    """
    Gets all tags or user tags.
    """

    # TODO Get favorite tags for the given user ID

    tags = Tag.objects.get_not_empty_tags()
    tag_names = []
    for tag in tags:
        tag_names.append(tag.name)

    return HttpResponse(content=json.dumps(tag_names))


# TODO The result can be cached by the thread last update time
# TODO Test this
def api_get_thread_posts(request, opening_post_id):
    """
    Gets the JSON array of thread posts
    """

    opening_post = get_object_or_404(Post, id=opening_post_id)
    thread = opening_post.get_thread()
    posts = thread.get_replies()

    json_data = {
        'posts': [],
        'last_update': None,
    }
    json_post_list = []

    for post in posts:
        json_post_list.append(_get_post_data(post.id))
    json_data['last_update'] = datetime_to_epoch(thread.last_edit_time)
    json_data['posts'] = json_post_list

    return HttpResponse(content=json.dumps(json_data))


def api_get_post(request, post_id):
    """
    Gets the JSON of a post. This can be
    used as and API for external clients.
    """

    post = get_object_or_404(Post, id=post_id)

    json = serializers.serialize("json", [post], fields=(
        "pub_time", "_text_rendered", "title", "text", "image",
        "image_width", "image_height", "replies", "tags"
    ))

    return HttpResponse(content=json)


# TODO Add pub time and replies
def _get_post_data(post_id, format_type=DIFF_TYPE_JSON, request=None,
        include_last_update=False):
    if format_type == DIFF_TYPE_HTML:
        return get_post(request, post_id).content.strip()
    elif format_type == DIFF_TYPE_JSON:
        post = get_object_or_404(Post, id=post_id)
        post_json = {
            'id': post.id,
            'title': post.title,
            'text': post.text.rendered,
        }
        if post.image:
            post_json['image'] = post.image.url
            post_json['image_preview'] = post.image.url_200x150
        if include_last_update:
            post_json['bump_time'] = datetime_to_epoch(
                    post.thread_new.bump_time)
        return post_json
