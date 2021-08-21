from dotenv import load_dotenv

# vars used during development in this app module, as well as calnotify.sendlib
load_dotenv()

import requests
import os
import json
from calnotify.datelib import is_days_away, set_tz, format_date, parse_and_format_date, isoparse
from calnotify.sendlib import sendsms, sendmail

set_tz(os.environ['TZ'])

data = json.loads(requests.get(
    'https://api.planningcenteronline.com' +
    '/resources/v2/event_instances' +
    '?filter=future&order=starts_at&include=event' +
    '&where[tag_ids]=' + os.environ['PCOTAGID'] +
    '&per_page=' + os.environ['PCOPERPAGE'],
    auth=(os.environ['PCOAPPID'], os.environ['PCOSECRET'])).text)

# read events from response data and reindex it in a hash by (str)id
events = {}
for event in data['included']:
    if event['type'] != 'Event':
        continue
    events[event['id']] = event['attributes']

# read all instances from the response data
for instance in data['data']:
    days_away = 1
    start_dt = isoparse(instance['attributes']['starts_at'])
    if is_days_away(start_dt, days_away):
        ev = events[instance['relationships']['event']['data']['id']]
        print('email:')
        sendmail(os.environ['TESTMAILTO'],
                 os.environ['PREFIX'] + ev['name'] + ' at ' + format_date(start_dt),
                 """
Don't forget!  There is an event coming up in %s days!

Event: %s
Time: from %s to %s
Location: %s
""" % (days_away, ev['name'], format_date(start_dt),
       parse_and_format_date(instance['attributes']['ends_at']),
       instance['attributes']['location']))

        sendsms(os.environ['TESTSMSTO'],
                os.environ['PREFIX'] + ev['name'] + ' at ' + format_date(start_dt))
