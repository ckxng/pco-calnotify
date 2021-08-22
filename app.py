from dotenv import load_dotenv

# vars used during development in this app module, as well as calnotify.sendlib
load_dotenv()

import requests
import os
import json
import yaml
from calnotify.datelib import is_days_away, set_tz, format_date, isoparse
from calnotify.sendlib import sendsms, sendmail

set_tz(os.environ['TZ'])

notify_list = {}
with open('contacts.yaml', 'r') as file:
    for group in yaml.safe_load(file)['groups']:
        notify_list[group['days']] = group['contacts']


data = json.loads(requests.get(
    'https://api.planningcenteronline.com' +
    '/resources/v2/event_instances' +
    '?filter=future&order=starts_at&include=event_times,event' +
    '&where[tag_ids]=' + os.environ['PCOTAGID'] +
    '&per_page=' + os.environ['PCOPERPAGE'],
    auth=(os.environ['PCOAPPID'], os.environ['PCOSECRET'])).text)

# read events from response data and reindex it in a hash by (str)id
events = {}
event_times = {}
for included in data['included']:
    if included['type'] == 'Event':
        events[included['id']] = included['attributes']
    elif included['type'] == 'EventTime':
        event_times[included['id']] = included['attributes']


# read all instances from the response data
for instance in data['data']:
    # look up when this event starts
    start_dt = isoparse(instance['attributes']['starts_at'])

    # for each group in the notify list, is this event in the specified range?
    for days_away in notify_list.keys():
        if is_days_away(start_dt, days_away):
            ev = events[instance['relationships']['event']['data']['id']]

            # look inside the event for specific times
            # only notify about published times (not things like "setup" or "teardown")
            times = instance['relationships']['event_times']['data']
            for time in times:
                if event_times[time['id']]['visible_on_widget_and_ical']:
                    et_start_str = format_date(isoparse(event_times[time['id']]['starts_at']))
                    et_end_str = format_date(isoparse(event_times[time['id']]['ends_at']))

                    # notify all contacts in the notify list
                    for contact in notify_list[days_away]:
                        if contact['type'] == 'email':
                            print('email:', contact['to'])
                            sendmail(contact['to'],
                                     os.environ['PREFIX'] + ev['name'] + ' at ' + et_start_str,
                                     """
Don't forget!  There is an event coming up in %s days!

Event: %s
Time: from %s to %s
Location: %s
""" % (days_away, ev['name'], et_start_str, et_end_str, instance['attributes']['location']))

                        elif contact['type'] == 'sms':
                            print('sms:', contact['to'])
                            sendsms(contact['to'], os.environ['PREFIX'] + ev['name'] + ' at ' + et_start_str)
