from datetime import datetime, timedelta
import hashlib
from django.db import transaction
from django.db.models import Count
from django.template import RequestContext

from django.utils import timezone
from django.views.generic import View
from boards import utils
from boards.models import User, Post
from boards.models.post import SETTING_MODERATE
from boards.models.user import RANK_USER, Ban
import neboard
from info.models import RandomBanners

BAN_REASON_SPAM = 'Autoban: spam bot'

OLD_USER_AGE_DAYS = 90

PARAMETER_FORM = 'form'

#def _show_random_banners(self, request):
	


class BaseBoardView(View):

    def get_context_data(self, **kwargs):
        request = kwargs['request']
        context = self._default_context(request)
        context['version'] = neboard.settings.VERSION
        context['site_name'] = neboard.settings.SITE_NAME

        return context

    def _default_context(self, request):
        """Create context with default values that are used in most views"""

        context = RequestContext(request)

        user = self._get_user(request)
        context['user'] = user
        context['tags'] = user.get_sorted_fav_tags()
        context['posts_per_day'] = float(Post.objects.get_posts_per_day())
	context['random_banners'] = RandomBanners.objects.all().order_by('?')[:1]

        theme = self._get_theme(request, user)
        context['theme'] = theme
        context['theme_css'] = 'css/' + theme + '/base_page.css'

        # This shows the moderator panel
        moderate = user.get_setting(SETTING_MODERATE)
        if moderate == 'True':
            context['moderator'] = user.is_moderator()
        else:
            context['moderator'] = False

        return context

    def _get_user(self, request):
        """
        Get current user from the session. If the user does not exist, create
        a new one.
        """

        session = request.session
        if not 'user_id' in session:
            request.session.save()

            md5 = hashlib.md5()
            md5.update(session.session_key)
            new_id = md5.hexdigest()

            while User.objects.filter(user_id=new_id).exists():
                md5.update(str(timezone.now()))
                new_id = md5.hexdigest()

            time_now = timezone.now()
            user = User.objects.create(user_id=new_id, rank=RANK_USER,
                                       registration_time=time_now)

            self._delete_old_users()

            session['user_id'] = user.id
        else:
            user = User.objects.get(id=session['user_id'])

        return user

    def _get_theme(self, request, user=None):
        """
        Get user's CSS theme
        """

        if not user:
            user = self._get_user(request)
        theme = user.get_setting('theme')
        if not theme:
            theme = neboard.settings.DEFAULT_THEME

        return theme

    def _delete_old_users(self):
        """
        Delete users with no favorite tags and posted messages. These can be spam
        bots or just old user accounts
        """

        old_registration_date = datetime.now().date() - timedelta(
            OLD_USER_AGE_DAYS)

        for user in User.objects.annotate(tags_count=Count('fav_tags')).filter(
                tags_count=0).filter(
                registration_time__lt=old_registration_date):
            if not Post.objects.filter(user=user).exists():
                user.delete()

    @transaction.atomic
    def _ban_current_user(self, request):
        """
        Add current user to the IP ban list
        """

        ip = utils.get_client_ip(request)
        ban, created = Ban.objects.get_or_create(ip=ip)
        if created:
            ban.can_read = False
            ban.reason = BAN_REASON_SPAM
        ban.save()
    
 

