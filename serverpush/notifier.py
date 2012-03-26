'''
	Event notifier.
'''

import tornado.web

from exceptions import catch_exceptions

class Notifier(tornado.web.RequestHandler):
	@catch_exceptions
	def post(self):
		model = self.get_argument('model', None)
		id = self.get_argument('id', None)
		if model and id and self.tracker.event(model, id):
			self.write('ok')
		else:
			self.write('fail')
