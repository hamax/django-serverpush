'''
	
	High level and django integration code.
	
'''

from collections import deque
from bisect import bisect_left
import urllib
import time

from django.core.urlresolvers import resolve
from django.contrib.sessions.backends.db import SessionStore
from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.utils import translation

#
# The main class for event tracking
#
class EventTracker():
	def __init__(self):
		self.channels = {}
	
	# Called by protocol.py via server.py on a new connection
	# subscribing to channels
	def connect(self, conn):
		request = HttpRequest()
		request.path = conn.url
		request.path_info = conn.url #TODO: path_info is not always full path
		request.method = 'GET'
		request.GET = conn.GET
		request.COOKIES = conn.cookies
	
		# auth
		request.session = {}
		request.user = AnonymousUser()
		if conn.cookie_id:
			request.session = SessionStore(session_key = conn.cookie_id)
			if '_auth_user_id' in request.session:
				request.user = User.objects.get(id = request.session['_auth_user_id'])			
			
		filters = []
		
		# url resolve
		func, args, kwargs = resolve(conn.url)
		
		# get _update function
		try:
			func = getattr(__import__(func.__module__, globals(), locals(), [func.__name__ + '_update']), func.__name__ + '_update')
		except:
			func = None
			
		if func: # if function _update is defined
			filters += func(request, *args, **kwargs)
		
		for filter in filters:
			# resolve model to string
			model = filter['model'].__module__ + '.' + filter['model'].__name__
			# create a new channel for this model
			if model not in self.channels: self.channels[model] = Channel()
			# add filter to the channel
			self.channels[model].newFilter(conn, request, filter)
	
	# Called by protocol.py via server.py on disconnect
	# unsubscribing from channels
	def disconnect(self, conn):
		for channel in self.channels:
			if conn.id in self.channels[channel].connections: del self.channels[channel].connections[conn.id]
	
	# Called by notify.py as a callback via server.py on a new event
	# notifies other connections and returns success status
	def event(self, model, id):	
		#resolve model and id to object
		try:
			object = getattr(__import__(model.rsplit('.', 1)[0], globals(), locals(), [model.split('.')[-1]]), model.split('.')[-1]).objects.filter(pk = id)
		except:
			return False
		
		if not object.exists():
			return False
		
		# if no one is on the channel we might need to create it
		# it is important not to just skip it because of the history
		if model not in self.channels:
			self.channels[model] = Channel()
		
		# pass the job to the channel
		return self.channels[model].event(object)

#
# Channel is an element of event tracker
#
class Channel():
	def __init__(self):
		self.maxsize = 200
		self.history = deque(maxlen = self.maxsize)
		self.connections = {}
	
	# filter in this contex is actually a connection
	# ... but there can be more filters for same connections
	def newFilter(self, conn, request, filter):
		if conn.id not in self.connections: self.connections[conn.id] = []
		filter = {'name':filter['name'], 'params':filter['params'], 'serializer':filter.get('serializer', extract), 'data':filter['data'], 'conn':conn, 'request':request}
		self.connections[conn.id].append(filter)
		self.sendHistory(filter)
	
	# Called by EventTracker on new event
	def event(self, object):
		self.history.append((time.time(), object))
		
		buffer = SendBuffer()
		for conn in self.connections:
			for filter in self.connections[conn]:
				if object.filter(**filter['params']).exists():
					buffer.append(filter['conn'], self.serialize(filter, object))
		buffer.send()
		
		return True
	
	# Called by newFilter
	# sends history - events that happened after page was generated, but before javascript connected to the serverpush
	def sendHistory(self, filter):
		if len(self.history) == self.maxsize and self.history[0]['timestamp'] > filter['conn'].timestamp:
			filter['conn'].send_frame('EVENT', {'name':'refresh'}) #history has failed us
			return
		
		buffer = SendBuffer()
		start = bisect_left(self.history, (filter['conn'].timestamp, None))
		for i in range(start, len(self.history)):
			object = self.history[i][1]
			if object.filter(**filter['params']).exists():
				buffer.append(filter['conn'], self.serialize(filter, object))
		buffer.send()
	
	# Called by event and sendHistory
	# serializes data (calls the serializer with right parameters)
	def serialize(self, filter, object):
		translation.activate(translation.get_language_from_request(filter['request']))
		return {'name':filter['name'], 'payload':filter['serializer'](filter['request'], object[0], filter['data'])}

#
# Buffer to send all of the notifications at once - prevents race conditions
#
class SendBuffer():
	def __init__(self):
		self.buffer = []

	def append(self, conn, data):
		self.buffer.append([conn, data])

	def send(self):
		for package in self.buffer:
			package[0].send_frame('EVENT', package[1])

# Default serializer for data from database
def extract(request, object, fields):
	data = {}
	for field in fields:
		data[field] = eval(fields[field])
	return data

# Call the notifier on new event - used from outside of this app
# paramters can be either object or model and primary key
def ping_notifier(model, pk = None):
	# if it was called with only one argument we assume it is object
	if not pk:
		pk = model.pk
		model = model.__class__
	
	# call the notifier via http request
	try:
		urllib.urlopen('http://localhost:8014/%s/%s' % (model.__module__ + '.' + model.__name__, pk))
		return True
	except IOError:
		return False

# Serverpush needs to know when was page generated
def context_processor(request):
	return {'generated_timestamp':str(time.time())} #TODO: it should be calculated at the beggining of the request
