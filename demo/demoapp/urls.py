from django.conf.urls.defaults import *

urlpatterns = patterns('demo.demoapp.views',
	(r'^$', 'list'),
)
