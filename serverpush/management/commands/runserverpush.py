from os import path as op

import tornado.web
import tornadio
import tornadio.router
import tornadio.server

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
		router = tornadio.get_router(Connection)

		# configure the Tornado application
		application = tornado.web.Application(
			[(r"/", Notifier), router.route()],
			enabled_protocols = [
				'websocket',
				'xhr-multipart',
				'xhr-polling'
			],
			socket_io_port = settings.SERVERPUSH_PORT
		)

		try:
			tornadio.server.SocketServer(application)
		except KeyboardInterrupt:
			print "Ctr+C pressed; Exiting."
