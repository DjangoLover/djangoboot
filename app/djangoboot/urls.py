from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

admin.autodiscover()


urlpatterns = patterns('',
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^', include('home.urls', namespace='home')),
    url(r'^', include('accounts.urls', namespace='accounts')),
    url(r'^', include('boots.urls', namespace='boots')),
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += static('/static', document_root='static/extras/')
