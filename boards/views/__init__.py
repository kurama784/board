__author__ = 'neko259'

from django.views.decorators.cache import cache_page
from django.views.i18n import javascript_catalog


@cache_page(86400)
def cached_js_catalog(request, domain='djangojs', packages=None):
    return javascript_catalog(request, domain, packages)
