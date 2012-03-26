import logging
from os import path as op

import tornado.web
import tornadio2
import tornadio2.router
import tornadio2.server

from django.conf import settings
from django.core.management.base import BaseCommand

from serverpush.connection import Connection
from serverpush.notifier import Notifier
from serverpush.tracker import Tracker

logger = logging.getLogger('serverpush')

class Command(BaseCommand):
	def handle(self, *args, **options):
		# set tracker object
		Connection.tracker = Notifier.tracker = Tracker()

		# use the routes classmethod to build the correct resource
		router = tornadio2.router.TornadioRouter(Connection, {
			'enabled_protocols': [
				'websocket',
				'xhr-polling',
				'htmlfile'
			]
		})

		# configure the Tornado application
		application = tornado.web.Application(
			router.urls,
			socket_io_port = settings.SERVERPUSH_PORT
		)

		notifier = tornado.web.Application(
			[(r"/notify", Notifier)],
		)
		notifier.listen(settings.SERVERPUSH_NOTIFIER_PORT, 'localhost')

		# configure Tornadio log, serverpush log is configured in settings.py
		if settings.TORNADIO_LOG:
			handler = logging.FileHandler(settings.TORNADIO_LOG)
			handler.setFormatter(logging.Formatter('%(asctime)-6s:  %(levelname)s - %(message)s'))
			logging.getLogger().addHandler(handler)
		logging.getLogger().setLevel(logging.WARNING)

		while True:
			try:
				tornadio2.server.SocketServer(application)
			except KeyboardInterrupt:
				print "Ctr+C pressed; Exiting."
				break
			except Exception, e:
				logger.exception('%s', e)
