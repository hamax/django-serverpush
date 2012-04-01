'''
	Cache SQL results during one notification processing.
'''

from django.db.models.sql import compiler

cache = None

def _patch_execute_sql(func):
	def wrapper(cls, *args, **kwargs):
		if cache == None:
			return func(cls, *args, **kwargs)

		sql = cls.as_sql()

		if sql not in cache:
			val = func(cls, *args, **kwargs)

			if hasattr(val, '__iter__'):
				cache[sql] = list(val)
			else:
				return val

		return cache[sql]
	return wrapper

def patch():
	compilers = (
		compiler.SQLCompiler,
		compiler.SQLAggregateCompiler,
		compiler.SQLDateCompiler,
	)

	for c in compilers:
		c.execute_sql = _patch_execute_sql(c.execute_sql)

def cache_start():
	global cache
	cache = {}

def cache_stop():
	global cache
	cache = None
