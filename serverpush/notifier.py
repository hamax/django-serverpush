'''
	Event notifier.
'''

import tornado.web

class Notifier(tornado.web.RequestHandler):
	def post(self):
		model = self.get_argument('model', None)
		id = self.get_argument('id', None)
		if model and id and self.tracker.event(model, id):
			self.write('ok')
		else:
			self.write('fail')
