'''
	Event notifier.
'''

import pickle

import tornado.web

from cache import cache_start, cache_stop
from exceptions import catch_exceptions

class Notifier(tornado.web.RequestHandler):
	def post(self):
		model = self.get_argument('model', None)
		id = self.get_argument('id', None)

		cache_start()
		try:
			status = self._handle(model, id)
		except:
			status = False
		cache_stop()

		if status:
			self.write('ok')
		else:
			self.write('fail')

	@catch_exceptions
	def _handle(self, model, id):
		if model == None or id == None:
			return False

		return self.tracker.event(model, id)
