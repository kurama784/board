from django.shortcuts import render, redirect
from boards.forms import LoginForm, PlainErrorList
from boards.models import User
from boards.views.base import BaseBoardView, PARAMETER_FORM

__author__ = 'neko259'


class LoginView(BaseBoardView):

    def get(self, request, form=None):
        context = self.get_context_data(request=request)

        if not form:
            form = LoginForm()
        context[PARAMETER_FORM] = form

        return render(request, 'boards/login.html', context)

    def post(self, request):
        form = LoginForm(request.POST, request.FILES,
                         error_class=PlainErrorList)
        form.session = request.session

        if form.is_valid():
            user = User.objects.get(user_id=form.cleaned_data['user_id'])
            request.session['user_id'] = user.id
            return redirect('index')
        else:
            return self.get(request, form)
