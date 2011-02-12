import logging

import uuid
import eventlet
import rtjp_eventlet

from error import ExpectedException

class HookboxConn(object):
	logger = logging.getLogger('hookbox')

	def __init__(self, server, rtjp_conn, remote_addr):
		self._rtjp_conn = rtjp_conn
		self.server = server
		self.state = 'initial'
		self.cookies = None
		self.cookie_string = None
		self.cookie_id = None
		self.cookie_identifier = 'sessionid'
		self.url = '/'
		self.GET = {}
		self.timestamp = 0
		self.id = str(uuid.uuid4()).replace('-', '')
		self.remote_addr = remote_addr

	def send_frame(self, *args, **kw):
		try:
			self._rtjp_conn.send_frame(*args, **kw).wait()
		except Exception, e:
			if 'closed' in str(e).lower():
				pass
			else:
				self.logger.warn("Unexpected error: %s", e, exc_info=True)

	def send_error(self, *args, **kw):
		return self._rtjp_conn.send_error(*args, **kw)

	def _close(self):
		if self.state == 'connected':
			self.server.closed(self)

	def run(self):
		while True:
			try:
				self.logger.debug('%s waiting for a frame', self)
				fid, fname, fargs= self._rtjp_conn.recv_frame().wait()
			except rtjp_eventlet.errors.ConnectionLost, e:
				self.logger.debug('received connection lost error')
				break
			except:
				self.logger.warn("Error reading frame", exc_info=True)
				continue
			f = getattr(self, 'frame_' + fname, None)
			if f:
				try:
					f(fid, fargs)
				except ExpectedException, e:
					self.send_error(fid, e)
				except Exception, e:
					self.logger.warn("Unexpected error: %s", e, exc_info=True)
					self.send_error(fid, e)
			else:
				self._default_frame(fid, fname, fargs)
		# cleanup
		self.logger.debug('loop done')
		self.server.disconnect(self)

	def _default_frame(fid, fname, fargs):
		pass

	def frame_CONNECT(self, fid, fargs):
		if self.state != 'initial':
			return self.send_error(fid, "Already logged in")
		if 'url' not in fargs:
			raise ExpectedException("Missing url")
		
		if 'cookie_string' in fargs:
			self.cookie_string = fargs['cookie_string']
			self.cookies = parse_cookies(fargs['cookie_string'])
			self.cookie_id = self.cookies.get(self.cookie_identifier, None)
		
		self.url = fargs['url']
		try:
			self.GET = dict([p.split('=') for p in fargs['GET'][1:].split('&')])
		except:
			pass
		self.timestamp = float(fargs['timestamp'])
		
		self.server.connect(self)
		self.state = 'connected'
		self.send_frame('CONNECTED', {})

def parse_cookies(cookieString):
	output = {}
	for m in cookieString.split('; '):
		try:
			k,v = m.split('=', 1)
			output[k] = v
		except:
			continue
	return output
