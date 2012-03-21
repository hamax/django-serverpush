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

		try:
			if settings.SERVERPUSH_LOG:
				logging.getLogger().addHandler(logging.FileHandler(settings.SERVERPUSH_LOG))
			logging.getLogger().setLevel(logging.ERROR)
			tornadio2.server.SocketServer(application)
		except KeyboardInterrupt:
			print "Ctr+C pressed; Exiting."
