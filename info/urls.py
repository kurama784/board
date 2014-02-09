from django.conf.urls import patterns, url, include
from boards import views

js_info_dict = {
    'packages': ('boards',),
}

urlpatterns = patterns('',

    url(r'^$', 'info.views.index', name='index'),
    url(r'^$', 'info.views.menu', name='menu'),
    url(r'^$', 'info.views.main', name='main'),

)
