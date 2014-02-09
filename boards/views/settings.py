from django.db import transaction
from django.shortcuts import render, redirect

from boards.views.base import BaseBoardView, PARAMETER_FORM
from boards.forms import SettingsForm, ModeratorSettingsForm, PlainErrorList
from boards.models.post import SETTING_MODERATE


class SettingsView(BaseBoardView):

    def get(self, request):
        context = self.get_context_data(request=request)
        user = context['user']
        is_moderator = user.is_moderator()

        selected_theme = context['theme']

        if is_moderator:
            form = ModeratorSettingsForm(initial={
                'theme': selected_theme,
                'moderate': context['moderator']
            }, error_class=PlainErrorList)
        else:
            form = SettingsForm(initial={'theme': selected_theme},
                                error_class=PlainErrorList)

        context[PARAMETER_FORM] = form

        return render(request, 'boards/settings.html', context)

    def post(self, request):
        context = self.get_context_data(request=request)
        user = context['user']
        is_moderator = user.is_moderator()

        with transaction.atomic():
            if is_moderator:
                form = ModeratorSettingsForm(request.POST,
                                             error_class=PlainErrorList)
            else:
                form = SettingsForm(request.POST, error_class=PlainErrorList)

            if form.is_valid():
                selected_theme = form.cleaned_data['theme']

                user.save_setting('theme', selected_theme)

                if is_moderator:
                    moderate = form.cleaned_data['moderate']
                    user.save_setting(SETTING_MODERATE, moderate)

            return redirect('settings')
