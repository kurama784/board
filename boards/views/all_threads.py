import string

from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import render, redirect

from boards import utils
from boards.abstracts.paginator import get_paginator
from boards.forms import ThreadForm, PlainErrorList
from boards.models import Post, Thread, Ban, Tag
from boards.views.banned import BannedView
from boards.views.base import BaseBoardView, PARAMETER_FORM
from boards.views.posting_mixin import PostMixin
import neboard

PARAMETER_CURRENT_PAGE = 'current_page'

PARAMETER_PAGINATOR = 'paginator'

PARAMETER_THREADS = 'threads'

TEMPLATE = 'boards/posting_general.html'
DEFAULT_PAGE = 1


class AllThreadsView(PostMixin, BaseBoardView):

    def get(self, request, page=DEFAULT_PAGE, form=None):
        context = self.get_context_data(request=request)

        if not form:
            form = ThreadForm(error_class=PlainErrorList)

        paginator = get_paginator(self.get_threads(),
                                  neboard.settings.THREADS_PER_PAGE)
        paginator.current_page = int(page)

        threads = paginator.page(page).object_list

        context[PARAMETER_THREADS] = threads
        context[PARAMETER_FORM] = form

        self._get_page_context(paginator, context, page)

        return render(request, TEMPLATE, context)

    def post(self, request, page=DEFAULT_PAGE):
        form = ThreadForm(request.POST, request.FILES,
                          error_class=PlainErrorList)
        form.session = request.session

        if form.is_valid():
            return self._new_post(request, form)
        if form.need_to_ban:
            # Ban user because he is suspected to be a bot
            self._ban_current_user(request)

        return self.get(request, page, form)

    @staticmethod
    def _get_page_context(paginator, context, page):
        """
        Get pagination context variables
        """

        context[PARAMETER_PAGINATOR] = paginator
        context[PARAMETER_CURRENT_PAGE] = paginator.page(int(page))

    # TODO This method should be refactored
    @transaction.atomic
    def _new_post(self, request, form, opening_post=None, html_response=True):
        """
        Add a new thread opening post.
        """

        ip = utils.get_client_ip(request)
        is_banned = Ban.objects.filter(ip=ip).exists()

        if is_banned:
            if html_response:
                return redirect(BannedView().as_view())
            else:
                return

        data = form.cleaned_data

        title = data['title']
        text = data['text']

        text = self._remove_invalid_links(text)

        if 'image' in data.keys():
            image = data['image']
        else:
            image = None

        tags = []

        tag_strings = data['tags']

        if tag_strings:
            tag_strings = tag_strings.split(' ')
            for tag_name in tag_strings:
                tag_name = string.lower(tag_name.strip())
                if len(tag_name) > 0:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)

        post = Post.objects.create_post(title=title, text=text, ip=ip,
                                        image=image, tags=tags,
                                        user=self._get_user(request))

        thread_to_show = (opening_post.id if opening_post else post.id)

        if html_response:
            if opening_post:
                return redirect(
                    reverse('thread', kwargs={'post_id': thread_to_show}) +
                    '#' + str(post.id))
            else:
                return redirect('thread', post_id=thread_to_show)

    def get_threads(self):
        return Thread.objects.filter(archived=False).order_by('-bump_time')
