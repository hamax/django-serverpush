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
	version = '2.1.0',
	author = 'Ziga Ham',
	author_email = 'ziga.ham@gmail.com',
	packages = ['serverpush', 'serverpush.management', 'serverpush.management.commands'],
	scripts = [],
	url = 'http://github.com/hamax/django-serverpush/',
	license = license,
	description = 'Easy to use django server push solution',
	long_description = readme,
	requires = ['tornadio2', 'django'],
	install_requires = [
		'tornadio2 >= 0.0.2',
		'django >= 1.0.0'
	]
)
