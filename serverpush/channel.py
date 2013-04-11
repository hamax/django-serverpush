'''
	Channel sends notifications to users.
'''

import pickle
import time
import logging
from collections import deque
from bisect import bisect_left

from django.utils import translation

import cache

logger = logging.getLogger('serverpush')

class Channel():
	def __init__(self):
		self.maxsize = 200
		self.history = deque(maxlen = self.maxsize)
		self.connections = {}

	# Called from Tracker when a new user connects
	def newFilter(self, conn, filter):
		if conn.id not in self.connections: self.connections[conn.id] = []
		filter = {'name':filter['name'], 'params':filter['params'], 'serializer':filter.get('serializer', extract), 'vary':filter.get('vary'), 'data':filter['data'], 'conn':conn}
		self.connections[conn.id].append(filter)
		self.sendHistory(filter)

	# Called by Tracker on new event
	def event(self, object):
		self.history.append((time.time(), object))

		buffer = SendBuffer()
		for conn in self.connections:
			for filter in self.connections[conn]:
				if object.filter(**filter['params']).exists():
					try:
						buffer.append(filter['conn'], self.serialize(filter, object))
					except Exception, e:
						logger.exception(e)
		buffer.send()

		return True

	# Called by newFilter
	# sends history - events that happened after page was generated, but before javascript connected to the serverpush
	def sendHistory(self, filter):
		if not filter['conn'].timestamp:
			return

		if len(self.history) == self.maxsize and self.history[0][0] > filter['conn'].timestamp:
			filter['conn'].send({'name':'refresh'}) #history has failed us
			return

		buffer = SendBuffer()
		start = bisect_left(self.history, (filter['conn'].timestamp, None))
		for i in range(start, len(self.history)):
			object = self.history[i][1]
			if object.filter(**filter['params']).exists():
				try:
					buffer.append(filter['conn'], self.serialize(filter, object))
				except Exception, e:
					logger.exception(e)
		buffer.send()

	# Called by event and sendHistory
	# serializes data (calls the serializer with right parameters)
	def serialize(self, filter, object):
		lang = translation.get_language_from_request(filter['conn'].request)
		
		cache_key = None
		if filter['vary'] != None and cache.cache:
			cache_key = pickle.dumps((filter['serializer'], lang, filter['vary']))
			if cache_key in cache.cache:
				return cache.cache[cache_key]
		
		translation.activate(lang)
		data = {'name':filter['name'], 'payload':filter['serializer'](filter['conn'].request, object[0], filter['data'])}
		
		if cache_key:
			cache.cache[cache_key] = data
		return data

#
# Buffer to send all of the notifications at once
#
class SendBuffer():
	def __init__(self):
		self.buffer = []

	def append(self, conn, data):
		self.buffer.append([conn, data])

	def send(self):
		for package in self.buffer:
			package[0].send(package[1])

# Default serializer for data from database
def extract(request, object, fields):
	data = {}
	for field in fields:
		data[field] = eval(fields[field])
	return data
