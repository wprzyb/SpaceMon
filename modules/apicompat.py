__version__ = 1.0
__cacheable__ = True

import json
import ConfigParser
from application import config

CONFIG_KEY = 'module_apicompat'


def update_document(data):
       if not data.get('state'):
           data['state'] = {}
       data['open'] = data['state'].get('open', False)
       return data
