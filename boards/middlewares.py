from django.shortcuts import redirect
from boards import views, utils
from boards.models import Ban
from django.utils.html import strip_spaces_between_tags
from django.conf import settings

RESPONSE_CONTENT_TYPE = 'Content-Type'

TYPE_HTML = 'text/html'


class BanMiddleware:
    """
    This is run before showing the thread. Banned users don't need to see
    anything
    """

    def process_view(self, request, view_func, view_args, view_kwargs):

        if view_func != views.banned.BannedView.as_view:
            ip = utils.get_client_ip(request)
            bans = Ban.objects.filter(ip=ip)

            if bans.exists():
                ban = bans[0]
                if not ban.can_read:
                    return redirect('banned')


class MinifyHTMLMiddleware(object):
    def process_response(self, request, response):
        try:
            compress_html = settings.COMPRESS_HTML
        except AttributeError:
            compress_html = False

        if RESPONSE_CONTENT_TYPE in response\
            and TYPE_HTML in response[RESPONSE_CONTENT_TYPE] and compress_html:
            response.content = strip_spaces_between_tags(
                response.content.strip())
        return response