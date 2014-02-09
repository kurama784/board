from django.shortcuts import get_object_or_404, render
from boards import utils
from boards.models import Ban
from boards.views.base import BaseBoardView


class BannedView(BaseBoardView):

    def get(self, request):
        """Show the page that notifies that user is banned"""

        context = self.get_context_data(request=request)

        ban = get_object_or_404(Ban, ip=utils.get_client_ip(request))
        context['ban_reason'] = ban.reason
        return render(request, 'boards/staticpages/banned.html', context)
