from django.shortcuts import render_to_response
from django.template import RequestContext

from demo.demoapp.models import Data
from demo.serverpush.handlers import ping_notifier

def list(request):
	# increase the counter in the database
	data, created = Data.objects.get_or_create(id = 1)
	data.counter += 1
	data.save()
	
	# notify the serverpush
	ping_notifier(data)
	
	# show the counter
	hits = data.counter
	return render_to_response('demoapp/list.html', locals(), context_instance = RequestContext(request))

def list_update(request):
	# name: just gets forwarded to javascript clients
	# model: the model that you want to watch
	# params: the filter params - for witch objects you want to be notified
	# data: data to pass to the serializer, the default one takes list of fields
	return [{'name':'update', 'model':Data, 'params':{}, 'data':{'hits':'object.counter'}}]
	
def update(request):
	return [{'name':'global', 'model':Data, 'params':{}, 'data':{'hits':'object.counter'}}]

