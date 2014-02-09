from django.shortcuts import redirect, get_object_or_404
from django.db import transaction

from boards.views.base import BaseBoardView
from boards.views.mixins import RedirectNextMixin
from boards.models import Post


class DeletePostView(BaseBoardView, RedirectNextMixin):

    @transaction.atomic
    def get(self, request, post_id):
        user = self._get_user(request)
        post = get_object_or_404(Post, id=post_id)

        opening_post = post.is_opening()

        if user.is_moderator():
            # TODO Show confirmation page before deletion
            Post.objects.delete_post(post)

        if not opening_post:
            thread = post.thread_new
            return redirect('thread', post_id=thread.get_opening_post().id)
        else:
            return self.redirect_to_next(request)
