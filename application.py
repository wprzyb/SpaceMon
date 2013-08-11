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

from threading import Timer
import web
import sys
import json
import yaml
import time
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(('config.cfg', 'localconfig.cfg'))

yamldata = ''
with file(config.get('data', 'file'), 'r') as f:
	yamldata = f.read()

yamldata = yaml.load(yamldata)

# caching... we will pass "fake" data array and see what it changed...
# and merge added items every time
def caching_function(original_update_document, cache_time):
	def inside_function(data):
		curr_time = time.time()
		if inside_function.last_cache < curr_time:
			inside_function.cached_data = original_update_document({})
			inside_function.last_cache = curr_time + cache_time

		data.update(inside_function.cached_data)

		return data

	inside_function.cached_data = {}
	inside_function.last_cache = 0

	return inside_function

def main():
	web.config.debug = config.getboolean('application', 'debug')

	modules_enabled = {}
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

						function_pointer = caching_function(function_pointer, cache_time)
				except ConfigParser.NoOptionError:
					pass

				modules_enabled[module_name] = function_pointer
			except ImportError as e:
				print 'WARNING: can not import module "%s": %s' % (module_name, str(e))

	print 'Loaded modules: %s\n' % ', '.join(modules_enabled.keys())

	class index:
		def GET(self):
			data = yamldata.copy()

			for module_name, function_pointer in modules_enabled.iteritems():
				new_data = None
				try:
					new_data = function_pointer(data)
					data = new_data
				except Exception as e:
					print 'WARNING: module "%s" failed: %s' % (module_name, str(e))				

			web.header('Content-Type', 'application/json')
			return json.dumps(data)

	urls = (
		'/', index,
	)

	app = web.application(urls, globals())
	app.run()

if __name__ == '__main__':
	main()
