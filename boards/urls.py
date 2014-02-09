from django.conf.urls import patterns, url, include
from boards import views
from boards.rss import AllThreadsFeed, TagThreadsFeed, ThreadPostsFeed
from boards.views import api, tag_threads, all_threads, archived_threads, \
        login, settings, all_tags
from boards.views.authors import AuthorsView
from boards.views.delete_post import DeletePostView
from boards.views.ban import BanUserView
from boards.views.static import StaticPageView
from boards.views.post_admin import PostAdminView


js_info_dict = {
    'packages': ('boards',),
}

urlpatterns = patterns('',

    # /boards/
    url(r'^$', 'info.views.index', name='index'),
    url(r'^menu/$', 'info.views.menu', name='index'),
    url(r'^main/$', 'info.views.main', name='index'),
    url(r'^boards/$', all_threads.AllThreadsView.as_view(), name='boards'),
    # /boards/page/
    url(r'^page/(?P<page>\w+)/$', all_threads.AllThreadsView.as_view(),
        name='index'),

    url(r'^archive/$', archived_threads.ArchiveView.as_view(), name='archive'),
    url(r'^archive/page/(?P<page>\w+)/$',
        archived_threads.ArchiveView.as_view(), name='archive'),

    # login page
    url(r'^login/$', login.LoginView.as_view(), name='login'),

    # /boards/tag/tag_name/
    url(r'^tag/(?P<tag_name>\w+)/$', tag_threads.TagView.as_view(),
        name='tag'),
    # /boards/tag/tag_id/page/
    url(r'^tag/(?P<tag_name>\w+)/page/(?P<page>\w+)/$',
        tag_threads.TagView.as_view(), name='tag'),

    # /boards/thread/
    url(r'^thread/(?P<post_id>\w+)/$', views.thread.ThreadView.as_view(),
        name='thread'),
    url(r'^thread/(?P<post_id>\w+)/mode/(?P<mode>\w+)/$', views.thread.ThreadView
        .as_view(), name='thread_mode'),

    # /boards/post_admin/
    url(r'^post_admin/(?P<post_id>\w+)/$', PostAdminView.as_view(),
            name='post_admin'),

    url(r'^settings/$', settings.SettingsView.as_view(), name='settings'),
    url(r'^tags/$', all_tags.AllTagsView.as_view(), name='tags'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^authors/$', AuthorsView.as_view(), name='authors'),
    url(r'^delete/(?P<post_id>\w+)/$', DeletePostView.as_view(),
            name='delete'),
    url(r'^ban/(?P<post_id>\w+)/$', BanUserView.as_view(), name='ban'),

    url(r'^banned/$', views.banned.BannedView.as_view(), name='banned'),
    url(r'^staticpage/(?P<name>\w+)/$', StaticPageView.as_view(),
        name='staticpage'),

    # RSS feeds
    url(r'^rss/$', AllThreadsFeed()),
    url(r'^page/(?P<page>\w+)/rss/$', AllThreadsFeed()),
    url(r'^tag/(?P<tag_name>\w+)/rss/$', TagThreadsFeed()),
    url(r'^tag/(?P<tag_name>\w+)/page/(?P<page>\w+)/rss/$', TagThreadsFeed()),
    url(r'^thread/(?P<post_id>\w+)/rss/$', ThreadPostsFeed()),

    # i18n
    url(r'^jsi18n/$', 'boards.views.cached_js_catalog', js_info_dict,
        name='js_info_dict'),

    # API
    url(r'^api/post/(?P<post_id>\w+)/$', api.get_post, name="get_post"),
    url(r'^api/diff_thread/(?P<thread_id>\w+)/(?P<last_update_time>\w+)/$',
        api.api_get_threaddiff, name="get_thread_diff"),
    url(r'^api/threads/(?P<count>\w+)/$', api.api_get_threads,
            name='get_threads'),
    url(r'^api/tags/$', api.api_get_tags, name='get_tags'),
    url(r'^api/thread/(?P<opening_post_id>\w+)/$', api.api_get_thread_posts,
            name='get_thread'),
    url(r'^api/add_post/(?P<opening_post_id>\w+)/$', api.api_add_post,
            name='add_post'),

)
