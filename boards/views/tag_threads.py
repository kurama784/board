from django.shortcuts import get_object_or_404
from boards.models import Tag, Post
from boards.views.all_threads import AllThreadsView, DEFAULT_PAGE
from boards.views.mixins import DispatcherMixin, RedirectNextMixin
from boards.forms import ThreadForm, PlainErrorList

__author__ = 'neko259'


class TagView(AllThreadsView, DispatcherMixin, RedirectNextMixin):

    tag_name = None

    def get_threads(self):
        tag = get_object_or_404(Tag, name=self.tag_name)

        return tag.threads.filter(archived=False).order_by('-bump_time')

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)

        tag = get_object_or_404(Tag, name=self.tag_name)
        context['tag'] = tag

        return context

    def get(self, request, tag_name, page=DEFAULT_PAGE, form=None):
        self.tag_name = tag_name

        dispatch_result = self.dispatch_method(request)
        if dispatch_result:
            return dispatch_result
        else:
            return super(TagView, self).get(request, page, form)

    def post(self, request, tag_name, page=DEFAULT_PAGE):
        form = ThreadForm(request.POST, request.FILES,
                          error_class=PlainErrorList)
        form.session = request.session

        if form.is_valid():
            return self._new_post(request, form)
        if form.need_to_ban:
            # Ban user because he is suspected to be a bot
            self._ban_current_user(request)

        return self.get(request, tag_name, page, form)

    def subscribe(self, request):
        user = self._get_user(request)
        tag = get_object_or_404(Tag, name=self.tag_name)

        if not tag in user.fav_tags.all():
            user.add_tag(tag)

        return self.redirect_to_next(request)

    def unsubscribe(self, request):
        user = self._get_user(request)
        tag = get_object_or_404(Tag, name=self.tag_name)

        if tag in user.fav_tags.all():
            user.remove_tag(tag)

        return self.redirect_to_next(request)
