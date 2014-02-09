from boards.models import Thread
from boards.views.all_threads import AllThreadsView

__author__ = 'neko259'


class ArchiveView(AllThreadsView):

    def get_threads(self):
        return Thread.objects.filter(archived=True).order_by('-bump_time')

    def get_context_data(self, **kwargs):
        context = super(ArchiveView, self).get_context_data(**kwargs)

        context['archived'] = True

        return context
