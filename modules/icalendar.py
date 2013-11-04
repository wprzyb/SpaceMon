__version__ = 1.0
__cacheable__ = True

import urllib2
import json
import vobject
import datetime
import time
from application import config

CONFIG_KEY = 'module_icalendar'

def update_document(data):
	remote = urllib2.urlopen(config.get(CONFIG_KEY, 'url'), timeout=config.getint(CONFIG_KEY, 'timeout'))

	current_date = datetime.datetime.now()

	if not data.get('events'):
		data['events'] = []

	components = vobject.readOne(remote)

	for event in components.contents['vevent']:
		# could be datetime or just date
		e_date = event.dtstart.value

		if type(e_date) is datetime.date:
			e_date = datetime.datetime.combine(e_date, datetime.time(0, 0))
		else:
			e_date = e_date.replace(tzinfo=None)

		# compare with timezone data removed
		if e_date < current_date:
			continue

		data['events'].append({
			'name': event.summary.value,
			'type': 'calendarevent',
			'timestamp': int(time.mktime((event.dtstart.value.timetuple()))),
			'extra': event.description.value,
		})

	return data