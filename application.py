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

	modules_enabled = []
	for module_name, enabled in config.items('modules'):
		if config.getboolean('modules', module_name):
			try:
				__import__('modules.%s' % module_name)
				modules_enabled.append(module_name)
			except ImportError:
				pass

	print 'Loaded modules: %s\n' % ','.join(modules_enabled)

	class index:
		def GET(self):
			data = yamldata

			for m in modules_enabled:
				new_data = None
				try:
					new_data = getattr(sys.modules['modules.%s' % m], 'update_document')(data)
					data = new_data
				except Exception as e:
					print 'Module "%s" failed: %s' % (m, str(e))				

			web.header('Content-Type', 'application/json')
			return json.dumps(data)

	urls = (
		'/', index,
	)

	app = web.application(urls, globals())
	app.run()

if __name__ == '__main__':
	main()
