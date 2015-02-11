# coding: utf-8

__version__ = 1.0
__cacheable__ = True

import urllib2
import json
import ConfigParser
from application import config

CONFIG_KEY = 'module_graphite'


def update_document(data):
	remote = urllib2.urlopen(config.get(CONFIG_KEY, 'url'), timeout=config.getint(CONFIG_KEY, 'timeout'))
	remote = json.load(remote)

	if not data.get('sensors'):
		data['sensors'] = {}
	
	if not data['sensors'].get('temperature'):
		data['sensors']['temperature'] = []
	if not data['sensors'].get('humidity'):
		data['sensors']['humidity'] = []
	if not data['sensors'].get('radiation'):
		data['sensors']['radiation'] = {}
		data['sensors']['radiation']['beta_gamma'] = []
	if not data['sensors'].get('barometer'):
		data['sensors']['barometer'] = []
                                                

	temp = {
		'value': '%.2f' % (float(remote[0]['datapoints'][0][0])),
		'unit': '°C',
		'location': 'Hardroom',
	}
	pressure = {
		'value': '%.2f' % (float(remote[1]['datapoints'][0][0])),
		'unit': 'hPA',
		'location': 'Hardroom',
	}
	hum = {
		'value': '%.2f' % (float(remote[2]['datapoints'][0][0])),
		'unit': '%',
		'location': 'Hardroom',
	}
	rad = {
		'value': '%.2f' % (float(remote[3]['datapoints'][0][0])),
		'unit': 'µSv/h',
		'location': 'Hardroom',
	}

	data['sensors']['temperature'].append(temp)
	data['sensors']['barometer'].append(pressure)
	data['sensors']['humidity'].append(hum)
	data['sensors']['radiation']['beta_gamma'].append(rad)

	return data
