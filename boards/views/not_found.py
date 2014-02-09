from django.shortcuts import render

from boards.views.base import BaseBoardView


class NotFoundView(BaseBoardView):
    """
    Page 404 (not found)
    """

    def get(self, request):
        context = self.get_context_data(request=request)
        return render(request, 'boards/404.html', context)
