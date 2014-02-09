from django.shortcuts import render

from boards.views.base import BaseBoardView
from boards.models.tag import Tag

class AllTagsView(BaseBoardView):

    def get(self, request):
        context = self.get_context_data(request=request)
        context['all_tags'] = Tag.objects.get_not_empty_tags()

        return render(request, 'boards/tags.html', context)
