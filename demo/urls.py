from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
	(r'^$', include('demo.demoapp.urls')),
)

if settings.LOCAL_DEVELOPMENT:
	urlpatterns += patterns("django.views",	url(r'^media/(?P<path>.*)$', "static.serve", {"document_root": settings.MEDIA_ROOT}))
