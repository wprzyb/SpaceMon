__version__ = 1.0
__cacheable__ = True

import urllib2
import json
import ConfigParser
from application import config

CONFIG_KEY = 'module_whois'


def update_document(data):
	remote = urllib2.urlopen(config.get(CONFIG_KEY, 'url'), timeout=config.getint(CONFIG_KEY, 'timeout'))

	whois_data = json.loads(remote.read())

	try:
		if config.get(CONFIG_KEY, 'overwrite_open'): # DEPRECATED
			if not data.get('state'):
				data['state'] = {}
			data['state'] = {'open': len(whois_data['users']) > 0}
	except ConfigParser.NoOptionError:
		pass

	if config.get(CONFIG_KEY, 'update_open'):
		if not data.get('state'):
			data['state'] = {}
		data['state']['open'] = len(whois_data['users']) > 0 or data['state'].get('open', False)
	
	if not data.get('sensors'):
		data['sensors'] = {}

	if not data['sensors'].get('people_now_present'):
		data['sensors']['people_now_present'] = []

	people_data = {
		'value': len(whois_data['users'])
	}

	if len(whois_data['users']) > 0:
		people_data['names'] = whois_data['users']

	data['sensors']['people_now_present'].append(people_data)

	return data