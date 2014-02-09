import string
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect
from boards import utils
from boards.forms import PostForm, PlainErrorList
from boards.models import Post, Ban, Tag
from boards.views.banned import BannedView
from boards.views.base import BaseBoardView, PARAMETER_FORM
from boards.views.posting_mixin import PostMixin
import neboard

MODE_GALLERY = 'gallery'
MODE_NORMAL = 'normal'


class ThreadView(BaseBoardView, PostMixin):

    def get(self, request, post_id, mode=MODE_NORMAL, form=None):
        opening_post = get_object_or_404(Post, id=post_id)

        # If this is not OP, don't show it as it is
        if not opening_post.is_opening():
            raise Http404

        if not form:
            form = PostForm(error_class=PlainErrorList)

        thread_to_show = opening_post.get_thread()

        context = self.get_context_data(request=request)

        context[PARAMETER_FORM] = form
        context["last_update"] = utils.datetime_to_epoch(
            thread_to_show.last_edit_time)
        context["thread"] = thread_to_show

        if MODE_NORMAL == mode:
            context['bumpable'] = thread_to_show.can_bump()
            if context['bumpable']:
                context['posts_left'] = neboard.settings.MAX_POSTS_PER_THREAD \
                        - thread_to_show.get_reply_count()
                context['bumplimit_progress'] = str(
                    float(context['posts_left']) /
                    neboard.settings.MAX_POSTS_PER_THREAD * 100)

            context['opening_post'] = opening_post

            document = 'boards/thread.html'
        elif MODE_GALLERY == mode:
            posts = thread_to_show.get_replies()
            context['posts'] = posts.filter(image_width__gt=0)

            document = 'boards/thread_gallery.html'
        else:
            raise Http404

        return render(request, document, context)

    def post(self, request, post_id, mode=MODE_NORMAL):
        opening_post = get_object_or_404(Post, id=post_id)

        # If this is not OP, don't show it as it is
        if not opening_post.is_opening():
            raise Http404

        if not opening_post.get_thread().archived:
            form = PostForm(request.POST, request.FILES,
                            error_class=PlainErrorList)
            form.session = request.session

            if form.is_valid():
                return self.new_post(request, form, opening_post)
            if form.need_to_ban:
                # Ban user because he is suspected to be a bot
                self._ban_current_user(request)

            return self.get(request, post_id, mode, form)

    @transaction.atomic
    def new_post(self, request, form, opening_post=None, html_response=True):
        """Add a new post (in thread or as a reply)."""

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

        post_thread = opening_post.get_thread()

        post = Post.objects.create_post(title=title, text=text, ip=ip,
                                        thread=post_thread, image=image,
                                        tags=tags,
                                        user=self._get_user(request))

        thread_to_show = (opening_post.id if opening_post else post.id)

        if html_response:
            if opening_post:
                return redirect(reverse(
                    'thread',
                    kwargs={'post_id': thread_to_show}) + '#' + str(post.id))
