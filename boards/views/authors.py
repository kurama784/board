from django.shortcuts import render

from boards.authors import authors
from boards.views.base import BaseBoardView


class AuthorsView(BaseBoardView):

    def get(self, request):
        context = self.get_context_data(request=request)
        context['authors'] = authors

        return render(request, 'boards/authors.html', context)
