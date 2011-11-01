'''
	Client functions (for django application).
'''

import urllib
import time

from django.conf import settings

# Call the notifier on new event
# paramters can be either object or model and primary key
def ping_notifier(model, pk = None):
	# if it was called with only one argument we assume it is object
	if not pk:
		pk = model.pk
		model = model.__class__

	data = {
		'model': model.__module__ + '.' + model.__name__,
		'id': pk
	}

	# call the notifier via http request
	try:
		urllib.urlopen('http://localhost:%d/notify' % settings.SERVERPUSH_NOTIFIER_PORT, urllib.urlencode(data))
		return True
	except IOError:
		return False

# Serverpush needs to know when was page generated
def context_processor(request):
	# TODO(hamax): time should be calculated at the beggining of the request
	return {'generated_timestamp':str(time.time())}
