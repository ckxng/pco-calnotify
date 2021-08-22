from dotenv import load_dotenv

# vars used during development in this app module, as well as calnotify.sendlib
load_dotenv()

import requests
import os
import json
import yaml
from calnotify.datelib import is_days_away, set_tz, format_date, parse_and_format_date, isoparse
from calnotify.sendlib import sendsms, sendmail

set_tz(os.environ['TZ'])

notify_list = {}
with open('contacts.yaml', 'r') as file:
    for group in yaml.safe_load(file)['groups']:
        notify_list[group['days']] = group['contacts']


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
    # look up when this event starts
    start_dt = isoparse(instance['attributes']['starts_at'])

    # for each group in the notify list, is this event in the specified range?
    for days_away in notify_list.keys():
        if is_days_away(start_dt, days_away):

            # notify all contacts in the notify list
            for contact in notify_list[days_away]:
                ev = events[instance['relationships']['event']['data']['id']]
                if contact['type'] == 'email':
                    print('email:', contact['to'])
                    sendmail(contact['to'],
                             os.environ['PREFIX'] + ev['name'] + ' at ' + format_date(start_dt),
                             """
Don't forget!  There is an event coming up in %s days!

Event: %s
Time: from %s to %s
Location: %s
""" % (days_away, ev['name'], format_date(start_dt),
       parse_and_format_date(instance['attributes']['ends_at']),
       instance['attributes']['location']))

                elif contact['type'] == 'sms':
                    print('sms:', contact['to'])
                    sendsms(contact['to'],
                            os.environ['PREFIX'] + ev['name'] + ' at ' + format_date(start_dt))
