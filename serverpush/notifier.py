'''
	Event notifier.
'''

import threading
import logging
import functools

import tornado.ioloop
import tornado.web
import tornado.httpserver

from django.conf import settings

logger = logging.getLogger('serverpush')

class Notifier(tornado.web.RequestHandler):
	def post(self):
		model = self.get_argument('model', None)
		id = self.get_argument('id', None)

		if model is None or id is None:
			logger.info('Malformed notification request.')
			self.write('model and id parameters are required')
			return

		tornado.ioloop.IOLoop.instance().add_callback(functools.partial(self.tracker.event, model, id))

		logger.info('Notification added to the queue (%d).', len(tornado.ioloop.IOLoop.instance()._callbacks))
		self.write('notification added to the queue')

class NotifierThread(threading.Thread):
	def run(self):
		ioloop = tornado.ioloop.IOLoop()
		application = tornado.web.Application(
			[(r"/notify", Notifier)],
		)
		http_server = tornado.httpserver.HTTPServer(application, io_loop=ioloop)
		http_server.listen(settings.SERVERPUSH_NOTIFIER_PORT, 'localhost')
		ioloop.start()
