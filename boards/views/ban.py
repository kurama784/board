from django.db import transaction
from django.shortcuts import get_object_or_404

from boards.views.base import BaseBoardView
from boards.models import Post, Ban
from boards.views.mixins import RedirectNextMixin


class BanUserView(BaseBoardView, RedirectNextMixin):

    @transaction.atomic
    def get(self, request, post_id):
        user = self._get_user(request)
        post = get_object_or_404(Post, id=post_id)

        if user.is_moderator():
            # TODO Show confirmation page before ban
            ban, created = Ban.objects.get_or_create(ip=post.poster_ip)
            if created:
                ban.reason = 'Banned for post ' + str(post_id)
                ban.save()

        return self.redirect_to_next(request)
