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
import ConfigParser

config = ConfigParser.ConfigParser()
config.read(('config.cfg', 'localconfig.cfg'))

yamldata = ''
with file(config.get('data', 'file'), 'r') as f:
	yamldata = f.read()

yamldata = yaml.load(yamldata)

def main():
	web.config.debug = config.getboolean('application', 'debug')

	modules_enabled = {}
	for module_name, enabled in config.items('modules'):
		if config.getboolean('modules', module_name):
			try:
				__import__('modules.%s' % module_name)
				function_pointer = getattr(sys.modules['modules.%s' % module_name], 'update_document')

				if not callable(function_pointer):
					print 'WARNING: modules.%s.update_document is not callable!' % module_name
					continue

				modules_enabled[module_name] = function_pointer
			except ImportError:
				pass

	print 'Loaded modules: %s\n' % ','.join(modules_enabled.keys())

	class index:
		def GET(self):
			data = yamldata

			for module_name, function_pointer in modules_enabled.iteritems():
				new_data = None
				try:
					new_data = function_pointer(data)
					data = new_data
				except Exception as e:
					print 'Module "%s" failed: %s' % (module_name, str(e))				

			web.header('Content-Type', 'application/json')
			return json.dumps(data)

	urls = (
		'/', index,
	)

	app = web.application(urls, globals())
	app.run()

if __name__ == '__main__':
	main()
