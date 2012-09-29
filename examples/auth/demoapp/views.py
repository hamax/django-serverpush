from django.shortcuts import render_to_response
from django.template import RequestContext

from serverpush.client import ping_notifier

from models import Data

def list(request):
	# increase the counter in the database
	data, created = Data.objects.get_or_create(id = 1)
	data.counter += 1
	data.save()

	# notify the serverpush
	ping_notifier(data)

	# show the counter
	hits = data.counter
	return render_to_response('list.html', locals(), context_instance = RequestContext(request))

def list_update(request):
	# check if the user is authenticated
	if not request.user.is_authenticated():
		print 'user is not authenticated'
		return []
	print 'user is authenticated (%s)' % request.user.username

	# name: name of the event in the javascript client code that we want to trigger (see counter.js)
	# model: the model that you want to watch
	# params: the filter params - for what objects you want to be notified
	# data: data to pass to the serializer, the default serializer takes a list of fields
	return [{'name':'update', 'model':Data, 'params':{}, 'data':{'hits':'object.counter'}}]
