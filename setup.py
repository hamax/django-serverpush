#!/usr/bin/env python

try:
	from setuptools import setup, find_packages
except ImportError:
	from distribute_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

try:
	license = open('LICENSE').read()
except:
	license = None

try:
	readme = open('README.md').read()
except:
	readme = None

setup(
	name = 'django-serverpush',
	version = '2.0.0',
	author = 'Ziga Ham',
	author_email = 'ziga.ham@gmail.com',
	packages = ['serverpush', 'serverpush.management', 'serverpush.management.commands'],
	scripts = [],
	url = 'http://github.com/hamax/django-serverpush/',
	license = license,
	description = 'Simple to use django serverpush solution',
	long_description = readme,
	requires = ['tornadio', 'django'],
	install_requires = [
		'tornadio == 0.0.4',
		'django >= 1.0.0'
	]
)