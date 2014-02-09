from django.shortcuts import render

from boards.views.base import BaseBoardView

class StaticPageView(BaseBoardView):

    def get(self, request, name):
        """
        Show a static page that needs only tags list and a CSS
        """

        context = self.get_context_data(request=request)
        return render(request, 'boards/staticpages/' + name + '.html', context)
