"""
This module contains helper functions and helper classes.
"""
from django.utils import timezone

from neboard import settings
import time


KEY_CAPTCHA_FAILS = 'key_captcha_fails'
KEY_CAPTCHA_DELAY_TIME = 'key_captcha_delay_time'
KEY_CAPTCHA_LAST_ACTIVITY = 'key_captcha_last_activity'


def need_include_captcha(request):
    """
    Check if request is made by a user.
    It contains rules which check for bots.
    """

    if not settings.ENABLE_CAPTCHA:
        return False

    enable_captcha = False

    #newcomer
    if KEY_CAPTCHA_LAST_ACTIVITY not in request.session:
        return settings.ENABLE_CAPTCHA

    last_activity = request.session[KEY_CAPTCHA_LAST_ACTIVITY]
    current_delay = int(time.time()) - last_activity

    delay_time = (request.session[KEY_CAPTCHA_DELAY_TIME]
                  if KEY_CAPTCHA_DELAY_TIME in request.session
                  else settings.CAPTCHA_DEFAULT_SAFE_TIME)

    if current_delay < delay_time:
        enable_captcha = True

    print 'ENABLING' + str(enable_captcha)

    return enable_captcha


def update_captcha_access(request, passed):
    """
    Update captcha fields.
    It will reduce delay time if user passed captcha verification and
    it will increase it otherwise.
    """
    session = request.session

    delay_time = (request.session[KEY_CAPTCHA_DELAY_TIME]
                  if KEY_CAPTCHA_DELAY_TIME in request.session
                  else settings.CAPTCHA_DEFAULT_SAFE_TIME)

    print "DELAY TIME = " + str(delay_time)

    if passed:
        delay_time -= 2 if delay_time >= 7 else 5
    else:
        delay_time += 10

    session[KEY_CAPTCHA_LAST_ACTIVITY] = int(time.time())
    session[KEY_CAPTCHA_DELAY_TIME] = delay_time


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def datetime_to_epoch(datetime):
    return int(time.mktime(timezone.localtime(
        datetime,timezone.get_current_timezone()).timetuple())
               * 1000000 + datetime.microsecond)