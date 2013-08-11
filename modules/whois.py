__version__ = 1.0

import urllib
import json
from application import config

def update_document(data):
	remote = urllib.urlopen(config.get('module_whois', 'url'))

	whois_data = json.loads(remote.read())

	if config.get('module_whois', 'overwrite_open'):
		data['state'] = {'open': len(whois_data['users']) > 0}
		
	data['sensors'] = {'people_now_present': [{
		'value': len(whois_data['users'])
	}]}

	if len(whois_data['users']) > 0:
		data['sensors']['people_now_present'][0]['names'] = whois_data['users']

	return data