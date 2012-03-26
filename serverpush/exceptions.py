import logging

from django.db import connection, DatabaseError

logger = logging.getLogger('serverpush')

def catch_exceptions(func):
	def wrapper(*arg, **kwarg):
		try:
			func(*arg, **kwarg)
		except DatabaseError:
			logger.warning('Database connection failed, trying to recover.')
			connection.connection.close()
			connection.connection = None
			raise
		except Exception, e:
			logger.exception('%s', e)
	return wrapper
