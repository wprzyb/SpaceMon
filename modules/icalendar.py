__version__ = 1.0
__cacheable__ = True

import urllib
import json
import vobject
import datetime
import time
from application import config

def update_document(data):
	remote = urllib.urlopen(config.get('module_icalendar', 'url'))

	current_date = datetime.datetime.now()

	if not data.get('events'):
		data['events'] = []

	while True:
		try:
			event = vobject.readOne(remote)
		except:
			break

		# compare with timezone data removed
		if event.vevent.dtstart.value.replace(tzinfo=None) < current_date:
			continue

		data['events'].append({
			'name': event.vevent.summary.value,
			'type': 'calendarevent',
			'timestamp': int(time.mktime((event.vevent.dtstart.value.timetuple()))),
			'extra': event.vevent.description.value,
		})

	remote.close()

	return data