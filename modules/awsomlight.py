__version__ = 1.0
__cacheable__ = True

import urllib2
import json
from application import config

CONFIG_KEY = 'module_awsomlight'

def update_document(data):
	remote = urllib2.urlopen(config.get(CONFIG_KEY, 'url'), timeout=config.getint(CONFIG_KEY, 'timeout')).read()
	
	if not data.get('sensors'):
		data['sensors'] = {}

	lights_data = {}

	if config.get(CONFIG_KEY, 'update_open'):
		is_open = False

		i = 0
		for m in config.get(CONFIG_KEY, 'update_open_lightmask'):
			if m == '1' and remote[i] == '1':
				is_open = True

				break

			i += 1

		if not data.get('state'):
			data['state'] = {}

		data['state']['open'] = is_open or data['state'].get('open', False)


	if not data['sensors'].get('ext_lights'):
		data['sensors']['ext_lights'] = []
	
	lights = {}
	for key, val in config.items(CONFIG_KEY):
		if key.startswith('name_'):
			lights[val] = remote[int(key[5:])] == '1'
	data['sensors']['ext_lights'].append(lights)
		
	return data
