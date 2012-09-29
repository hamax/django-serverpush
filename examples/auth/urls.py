from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
	url(r'^login$', 'django.contrib.auth.views.login'),
	url(r'^$', 'auth.demoapp.views.list'),
)
