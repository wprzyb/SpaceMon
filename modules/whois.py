__version__ = 1.0
__cacheable__ = True

import urllib2
import json
from application import config

def update_document(data):
	remote = urllib2.urlopen(config.get('module_whois', 'url'), timeout=1)

	whois_data = json.loads(remote.read())

	if config.get('module_whois', 'overwrite_open'):
		data['state'] = {'open': len(whois_data['users']) > 0}
	
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