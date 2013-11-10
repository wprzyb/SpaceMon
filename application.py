# -*- coding: utf-8 -*-

# Appplication that responds to SpaceAPI [http://spaceapi.net] requests
# Copyright (C) 2013 Tadeusz Magura-Witkowski
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import json
import yaml
import time
import copy
import ConfigParser
from copy import deepcopy
from threading import Thread
from bottle import route, run, response

config = ConfigParser.ConfigParser()
config.read(('config.cfg', 'localconfig.cfg'))

yamldata = ''
with file(config.get('data', 'file'), 'r') as f:
	yamldata = f.read()

yamldata = yaml.load(yamldata)

def dict_merge(a, b):
	if not isinstance(b, dict):
		return b

	result = deepcopy(a)
	for k, v in b.iteritems():
		if k in result and isinstance(result[k], dict):
			result[k] = dict_merge(result[k], v)
		else:
			result[k] = deepcopy(v)

	return result


# caching... we will pass "fake" data array and see what it changed...
# and merge added items every time
# now with threading
class caching_class:
	def __init__(self, original_update_document, cache_time):
		self.original_update_document = original_update_document
		self.cache_time = cache_time

		self.last_cache = 0
		self.cached_data = {}

	# merge my data with dict
	def merge_with_data(self, data):
		newdata = dict_merge(data, self.cached_data)

		if config.getboolean('module_cache', 'or_state_open') and data.get('state', {'open': False}).get('open', False): # some module set it as OPEN, so it must remain OPEN
			newdata['state']['open'] = True

		return newdata

	__call__ = merge_with_data

	def is_run_needed(self):
		return self.last_cache < time.time()

	# run real module
	def run_module(self):
		self.cached_data = self.original_update_document({})
		self.last_cache = time.time() + self.cache_time

def main():
	modules_enabled = {}
	modules_parallel = {}

	for module_name, enabled in config.items('modules'):
		if config.getboolean('modules', module_name):
			try:
				__import__('modules.%s' % module_name)
				module = sys.modules['modules.%s' % module_name]
				function_pointer = getattr(module, 'update_document')

				if not callable(function_pointer):
					print 'WARNING: modules.%s.update_document is not callable!' % module_name
					continue

				try:
					cache_time = config.getint('module_cache', module_name)

					if cache_time:
						try:
							if not getattr(module, 'update_document', '__cacheable__'):
								print 'WARNING: module "%s" is not cacheable but caching enabled in config file... This can result in big boom!'
						except exceptions.AttributeError:
							print 'WARNING: module "%s" does not have __cacheable__ flag...'

						function_pointer = caching_class(function_pointer, cache_time)

						modules_parallel[module_name] = function_pointer
				except ConfigParser.NoOptionError:
					pass

				modules_enabled[module_name] = function_pointer

			except ImportError as e:
				print 'WARNING: can not import module "%s": %s' % (module_name, str(e))

	print 'Loaded modules: %s\n' % ', '.join(modules_enabled.keys())

	@route('/')
	def index():
		data = copy.deepcopy(yamldata)

		threads = []

		# run threads
		for module_name, function_pointer in modules_parallel.iteritems():
			if not function_pointer.is_run_needed():
				continue

			newt = Thread(None, function_pointer.run_module)
			newt.start()

			threads.append(newt)

		# wait for all to complete
		for thread_obj in threads:
			thread_obj.join()

		# will exec modules 
		# or exec merge for threaded modules
		for module_name, function_pointer in modules_enabled.iteritems():
			new_data = None
			try:
				new_data = function_pointer(copy.deepcopy(data))
				data = new_data
			except Exception as e:
				print 'WARNING: module "%s" failed: %s' % (module_name, str(e))				

		# response.charset = 'utf8'
		response.set_header('Content-Type', 'application/json')
		response.set_header('Access-Control-Allow-Origin', '*')
		response.set_header('Cache-Control', 'no-cache')
		return json.dumps(data)

	run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=config.getboolean('application', 'debug'))

if __name__ == '__main__':
	main()
