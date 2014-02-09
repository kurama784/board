PARAMETER_METHOD = 'method'

from django.shortcuts import redirect
from django.http import HttpResponseRedirect


class RedirectNextMixin:

    def redirect_to_next(self, request):
        """
        If a 'next' parameter was specified, redirect to the next page. This
        is used when the user is required to return to some page after the
        current view has finished its work.
        """

        if 'next' in request.GET:
            next_page = request.GET['next']
            return HttpResponseRedirect(next_page)
        else:
            return redirect('index')


class DispatcherMixin:
    """
    This class contains a dispather method that can run a method specified by
    'method' request parameter.
    """

    def dispatch_method(self, *args, **kwargs):
        request = args[0]

        method_name = None
        if PARAMETER_METHOD in request.GET:
            method_name = request.GET[PARAMETER_METHOD]
        elif PARAMETER_METHOD in request.POST:
            method_name = request.POST[PARAMETER_METHOD]

        if method_name:
            return getattr(self, method_name)(*args, **kwargs)
