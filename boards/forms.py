import re
import time
import hashlib

from captcha.fields import CaptchaField
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from boards.mdx_neboard import formatters
from boards.models.post import TITLE_MAX_LENGTH
from boards.models import User, Post
from neboard import settings
from boards import utils
import boards.settings as board_settings

ATTRIBUTE_PLACEHOLDER = 'placeholder'

LAST_POST_TIME = 'last_post_time'
LAST_LOGIN_TIME = 'last_login_time'
TEXT_PLACEHOLDER = _('''Type message here. You can reply to message >>123 like
 this. 2 new lines are required to start new paragraph.''')
TAGS_PLACEHOLDER = _('tag1 several_words_tag')

ERROR_IMAGE_DUPLICATE = _('Such image was already posted')

LABEL_TITLE = _('Title')
LABEL_TEXT = _('Text')
LABEL_TAG = _('Tag')

TAG_MAX_LENGTH = 20

REGEX_TAG = ur'^[\w\d]+$'


class FormatPanel(forms.Textarea):
    def render(self, name, value, attrs=None):
        output = '<div id="mark-panel">'
        for formatter in formatters:
            output += u'<span class="mark_btn"' + \
                      u' onClick="addMarkToMsg(\'' + formatter.format_left + \
                      '\', \'' + formatter.format_right + '\')">' + \
                      formatter.preview_left + formatter.name + \
                      formatter.preview_right + u'</span>'

        output += '</div>'
        output += super(FormatPanel, self).render(name, value, attrs=None)

        return output


class PlainErrorList(ErrorList):
    def __unicode__(self):
        return self.as_text()

    def as_text(self):
        return ''.join([u'(!) %s ' % e for e in self])


class NeboardForm(forms.Form):

    def as_div(self):
        """
        Returns this form rendered as HTML <as_div>s.
        """

        return self._html_output(
            # TODO Do not show hidden rows in the list here
            normal_row='<div class="form-row">'
                       '<div class="form-label">'
                       '%(label)s'
                       '</div>'
                       '<div class="form-input">'
                       '%(field)s'
                       '</div>'
                       '%(help_text)s'
                       '</div>',
            error_row='<div class="form-row">'
                      '<div class="form-label"></div>'
                      '<div class="form-errors">%s</div>'
                      '</div>',
            row_ender='</div>',
            help_text_html='%s',
            errors_on_separate_row=True)

    def as_json_errors(self):
        errors = []

        for name, field in self.fields.items():
            if self[name].errors:
                errors.append({
                    'field': name,
                    'errors': self[name].errors.as_text(),
                })

        return errors


class PostForm(NeboardForm):

    title = forms.CharField(max_length=TITLE_MAX_LENGTH, required=False,
                            label=LABEL_TITLE)
    text = forms.CharField(
        widget=FormatPanel(attrs={ATTRIBUTE_PLACEHOLDER: TEXT_PLACEHOLDER}),
        required=False, label=LABEL_TEXT)
    image = forms.ImageField(required=False, label=_('Image'))

    # This field is for spam prevention only
    email = forms.CharField(max_length=100, required=False, label=_('e-mail'),
                            widget=forms.TextInput(attrs={
                                'class': 'form-email'}))

    session = None
    need_to_ban = False

    def clean_title(self):
        title = self.cleaned_data['title']
        if title:
            if len(title) > TITLE_MAX_LENGTH:
                raise forms.ValidationError(_('Title must have less than %s '
                                              'characters') %
                                            str(TITLE_MAX_LENGTH))
        return title

    def clean_text(self):
        text = self.cleaned_data['text']
        if text:
            if len(text) > board_settings.MAX_TEXT_LENGTH:
                raise forms.ValidationError(_('Text must have less than %s '
                                              'characters') %
                                            str(board_settings
                                            .MAX_TEXT_LENGTH))
        return text

    def clean_image(self):
        image = self.cleaned_data['image']
        if image:
            if image._size > board_settings.MAX_IMAGE_SIZE:
                raise forms.ValidationError(
                    _('Image must be less than %s bytes')
                    % str(board_settings.MAX_IMAGE_SIZE))

            md5 = hashlib.md5()
            for chunk in image.chunks():
                md5.update(chunk)
            image_hash = md5.hexdigest()
            if Post.objects.filter(image_hash=image_hash).exists():
                raise forms.ValidationError(ERROR_IMAGE_DUPLICATE)

        return image

    def clean(self):
        cleaned_data = super(PostForm, self).clean()

        if not self.session:
            raise forms.ValidationError('Humans have sessions')

        if cleaned_data['email']:
            self.need_to_ban = True
            raise forms.ValidationError('A human cannot enter a hidden field')

        if not self.errors:
            self._clean_text_image()

        if not self.errors and self.session:
            self._validate_posting_speed()

        return cleaned_data

    def _clean_text_image(self):
        text = self.cleaned_data.get('text')
        image = self.cleaned_data.get('image')

        if (not text) and (not image):
            error_message = _('Either text or image must be entered.')
            self._errors['text'] = self.error_class([error_message])

    def _validate_posting_speed(self):
        can_post = True

        if LAST_POST_TIME in self.session:
            now = time.time()
            last_post_time = self.session[LAST_POST_TIME]

            current_delay = int(now - last_post_time)

            if current_delay < settings.POSTING_DELAY:
                error_message = _('Wait %s seconds after last posting') % str(
                    settings.POSTING_DELAY - current_delay)
                self._errors['text'] = self.error_class([error_message])

                can_post = False

        if can_post:
            self.session[LAST_POST_TIME] = time.time()


class ThreadForm(PostForm):

    regex_tags = re.compile(ur'^[\w\s\d]+$', re.UNICODE)

    tags = forms.CharField(
        widget=forms.TextInput(attrs={ATTRIBUTE_PLACEHOLDER: TAGS_PLACEHOLDER}),
        max_length=100, label=_('Tags'))

    def clean_tags(self):
        tags = self.cleaned_data['tags']

        if tags:
            if not self.regex_tags.match(tags):
                raise forms.ValidationError(
                    _('Inappropriate characters in tags.'))

        return tags

    def clean(self):
        cleaned_data = super(ThreadForm, self).clean()

        return cleaned_data


class PostCaptchaForm(PostForm):
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs['request']
        del kwargs['request']

        super(PostCaptchaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(PostCaptchaForm, self).clean()

        success = self.is_valid()
        utils.update_captcha_access(self.request, success)

        if success:
            return cleaned_data
        else:
            raise forms.ValidationError(_("Captcha validation failed"))


class ThreadCaptchaForm(ThreadForm):
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        self.request = kwargs['request']
        del kwargs['request']

        super(ThreadCaptchaForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(ThreadCaptchaForm, self).clean()

        success = self.is_valid()
        utils.update_captcha_access(self.request, success)

        if success:
            return cleaned_data
        else:
            raise forms.ValidationError(_("Captcha validation failed"))


class SettingsForm(NeboardForm):

    theme = forms.ChoiceField(choices=settings.THEMES,
                              label=_('Theme'))


class ModeratorSettingsForm(SettingsForm):

    moderate = forms.BooleanField(required=False, label=_('Enable moderation '
                                                          'panel'))


class LoginForm(NeboardForm):

    user_id = forms.CharField()

    session = None

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if user_id:
            users = User.objects.filter(user_id=user_id)
            if len(users) == 0:
                raise forms.ValidationError(_('No such user found'))

        return user_id

    def _validate_login_speed(self):
        can_post = True

        if LAST_LOGIN_TIME in self.session:
            now = time.time()
            last_login_time = self.session[LAST_LOGIN_TIME]

            current_delay = int(now - last_login_time)

            if current_delay < board_settings.LOGIN_TIMEOUT:
                error_message = _('Wait %s minutes after last login') % str(
                    (board_settings.LOGIN_TIMEOUT - current_delay) / 60)
                self._errors['user_id'] = self.error_class([error_message])

                can_post = False

        if can_post:
            self.session[LAST_LOGIN_TIME] = time.time()

    def clean(self):
        if not self.session:
            raise forms.ValidationError('Humans have sessions')

        self._validate_login_speed()

        cleaned_data = super(LoginForm, self).clean()

        return cleaned_data


class AddTagForm(NeboardForm):

    tag = forms.CharField(max_length=TAG_MAX_LENGTH, label=LABEL_TAG)
    method = forms.CharField(widget=forms.HiddenInput(), initial='add_tag')

    def clean_tag(self):
        tag = self.cleaned_data['tag']

        regex_tag = re.compile(REGEX_TAG, re.UNICODE)
        if not regex_tag.match(tag):
            raise forms.ValidationError(_('Inappropriate characters in tags.'))

        return tag

    def clean(self):
        cleaned_data = super(AddTagForm, self).clean()

        return cleaned_data

