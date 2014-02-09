# Django settings for neboard project.
import os
from boards.mdx_neboard import markdown_extended

DEBUG = False
TEMPLATE_DEBUG = DEBUG
SERVER_DIR = '/domains/rikuchan.tk/public_html/rikuchan'

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
    ('admin', 'admin@example.com')
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'database.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
	'CONN_MAX_AGE': None,
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = SERVER_DIR + '/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
# It is really a hack, put real paths, not related
STATICFILES_DIRS = (
    SERVER_DIR + '/static/boards',
    SERVER_DIR  + '/static/info',

#    '/d/work/python/django/neboard/neboard/boards/static',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

if DEBUG:
    STATICFILES_STORAGE = \
        'django.contrib.staticfiles.storage.StaticFilesStorage'
else:
    STATICFILES_STORAGE = \
        'django.contrib.staticfiles.storage.CachedStaticFilesStorage'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@1rc$o(7=tt#kd+4s$u6wchm**z^)4x90)7f6z(i&amp;55@o11*8o'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'boards.middlewares.BanMiddleware',
    'boards.middlewares.MinifyHTMLMiddleware',
)

ROOT_URLCONF = 'neboard.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'neboard.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    SERVER_DIR + 'templates/boards/',
    SERVER_DIR + 'templates/info/'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    # 'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
     'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'django.contrib.humanize',
    'django_cleanup',
    'boards',
    'captcha',
    'south',
    'info',
    'sorl.thumbnail',
    #'debug_toolbar',
)

# TODO: NEED DESIGN FIXES
CAPTCHA_OUTPUT_FORMAT = (u' %(hidden_field)s '
                         u'<div class="form-label">%(image)s</div>'
                         u'<div class="form-text">%(text_field)s</div>')

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

MARKUP_FIELD_TYPES = (
    ('markdown', markdown_extended),
)
# Custom imageboard settings
# TODO These should me moved to
MAX_POSTS_PER_THREAD = 200  # Thread bumplimit
MAX_THREAD_COUNT = 5  # Old threads will be deleted to preserve this count
THREADS_PER_PAGE = 5
SITE_NAME = 'Riku-chan'

THEMES = [
    ('riku_chan', 'Default'),
    ('pg', 'Photon'),
    ('md', 'Night'),
    ('md_centered', 'Night (centered)'),
    ('dark_red', 'Dark Red'),
    ('light_red', 'Light Pomidorka'),
    ('light_blue', 'Light Blue'),
    ('hack', 'GreenHack'),
    ('space', 'Space'),
    ('sw', 'Blue White'),
]

DEFAULT_THEME = 'riku_chan'

POPULAR_TAGS = 10
LAST_REPLIES_COUNT = 3

ENABLE_CAPTCHA = False
# if user tries to post before CAPTCHA_DEFAULT_SAFE_TIME. Captcha will be shown
CAPTCHA_DEFAULT_SAFE_TIME = 30  # seconds
POSTING_DELAY = 20  # seconds

COMPRESS_HTML = True

VERSION = '0.1'

# Debug mode middlewares
if DEBUG:

    SITE_NAME += ' Imageboard(Debug)'

    MIDDLEWARE_CLASSES += (
        'boards.profiler.ProfilerMiddleware',
    )

    def custom_show_toolbar(request):
        return DEBUG

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
        'HIDE_DJANGO_SQL': False,
        'ENABLE_STACKTRACES': True,
    }

    # FIXME Uncommenting this fails somehow. Need to investigate this
    #DEBUG_TOOLBAR_PANELS += (
    #    'debug_toolbar.panels.profiling.ProfilingDebugPanel',
    #)

THUMBNAIL_DEBUG = False
