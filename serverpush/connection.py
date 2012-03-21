'''
	Tornadio connection.
'''

import json

import tornadio2

from django.http import HttpRequest
from django.contrib.auth.models import User
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.db import SessionStore

class Connection(tornadio2.SocketConnection):
	def __init__(self, *args, **kwargs):
		super(Connection, self).__init__(*args, **kwargs)
		self.handshake = True

	@tornadio2.event('login')
	def login(self, **message):
		if not self.handshake:
			pass
		else:
			try:
				self.timestamp = float(message['timestamp'])
			except:
				self.timestamp = None

			self.request = HttpRequest()
			self.request.path = message.get('url', '/')
			# TODO(hamax): path_info is not always full path
			self.request.path_info = self.request.path
			self.request.method = 'GET'
			self.request.GET = parse_params(message.get('GET', ''))
			self.request.COOKIES = parse_cookies(message.get('cookies', ''))
			# set to XMLHttpRequest so that request.is_ajax() returns True
			self.request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

			# auth
			self.request.session = {}
			self.request.user = AnonymousUser()
			if 'sessionid' in self.request.COOKIES:
				self.request.session = SessionStore(session_key = self.request.COOKIES['sessionid'])
				if '_auth_user_id' in self.request.session:
					self.request.user = User.objects.get(id = self.request.session['_auth_user_id'])

			self.handshake = False
			self.tracker.connect(self)

	@tornadio2.event('stats')
	def stats(self):
  		return self.session.server.stats.dump()

	def on_close(self):
		if not self.handshake:
			self.tracker.disconnect(self)

def parse_params(params):
	try:
		return dict([p.split('=') for p in params[1:].split('&')])
	except:
		return {}

def parse_cookies(cookieString):
	output = {}
	for m in cookieString.split('; '):
		try:
			k,v = m.split('=', 1)
			output[k] = v
		except:
			continue
	return output
