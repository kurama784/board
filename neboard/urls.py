from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings as conf
from neboard import settings

from boards.views.not_found import NotFoundView

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'neboard.views.home', name='home'),
    # url(r'^neboard/', include('neboard.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('boards.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = NotFoundView.as_view()
