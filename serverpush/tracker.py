'''
	Tracker groups connections and events into channels.
'''

from django.conf import settings
from django.core.urlresolvers import resolve

from channel import Channel

class Tracker():
	def __init__(self):
		# Channels
		self.channels = {}

		# Global filter functions
		self.globals = []
		for func_path in settings.SERVERPUSH_GLOBALS:
			self.globals.append(getattr(__import__(func_path.rsplit('.', 1)[0], globals(), locals(), [func_path.rsplit('.', 1)[-1]]), func_path.rsplit('.', 1)[-1]))

		self.next_id = 1

	# Connection calls this method to register itself
	def connect(self, conn):
		# assign id to the connection
		conn.id = self.next_id
		self.next_id += 1

		# get global filters
		filters = []
		for func in self.globals:
			filters += func(conn.request)

		# url resolve
		func, args, kwargs = resolve(conn.request.path)

		# get _update function
		try:
			func = getattr(__import__(func.__module__, globals(), locals(), [func.__name__ + '_update']), func.__name__ + '_update')
		except:
			func = None

		if func: # if function _update is defined
			filters += func(conn.request, *args, **kwargs)

		for filter in filters:
			# resolve model to string
			model = filter['model'].__module__ + '.' + filter['model'].__name__
			# create a new channel for this model
			if model not in self.channels: self.channels[model] = Channel()
			# add filter to the channel
			self.channels[model].newFilter(conn, filter)

	# Connection calls this method to unregister itself
	def disconnect(self, conn):
		for channel in self.channels:
			if conn.id in self.channels[channel].connections:
				del self.channels[channel].connections[conn.id]

	# Called by notify.py as a callback via server.py on a new event
	# notifies other connections and returns success status
	def event(self, model, id):
		# resolve model and id to object
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
