import sys
from cStringIO import StringIO
from django.conf import settings
import line_profiler


class ProfilerMiddleware(object):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        if settings.DEBUG and 'prof' in request.GET:
            self.profiler = line_profiler.LineProfiler()
            self.profiler.add_function(callback)
            self.profiler.enable()
            args = (request,) + callback_args
            return callback(*args, **callback_kwargs)

    def process_response(self, request, response):
        if settings.DEBUG and 'prof' in request.GET:
            out = StringIO()
            old_stdout, sys.stdout = sys.stdout, out
            self.profiler.print_stats()
            sys.stdout = old_stdout
            response.content = '<pre>%s</pre>' % out.getvalue()
        return response
