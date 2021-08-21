from dotenv import load_dotenv
import requests
import os
import pytz
import json
import datetime
from dateutil.parser import isoparse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client

load_dotenv()

tz = pytz.timezone(os.environ['TZ'])
date_fmt = "%m/%d/%Y at %I:%M:%S %p"


def is_days_away(dt, days) -> bool:
    """
    Test to see if a datetime is more than days away, but less than days-1 from now.
    :rtype: bool
    :param dt: datetime object to compare
    :param days: the number of days away the time must be
    :return: True if *dt* is *days* days away, else False
    """
    now = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    day = datetime.timedelta(days=1)
    return dt - ((days + 1) * day) < now < dt - (days * day)


def sendmail(to, subject, text):
    """
    Send a plain text email
    :param to: the email address to send to
    :param subject: the email subject
    :param text: the plain text message to send
    """
    message = Mail(
        from_email=os.environ['MAILFROM'],
        to_emails=to,
        subject=subject,
        plain_text_content=text)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRIDAPIKEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def sendsms(to, text):
    """
    Sends a SMS
    :param to: phone number in string format matching +15551234567
    :param text: the plain text message to send
    """
    client = Client(os.environ.get('TWILIOSID'), os.environ.get('TWILIOTOKEN'))

    message = client.messages.create(
        messaging_service_sid=os.environ.get('TWILIOSERVICESID'),
        body=text,
        to=to
    )

    print(message.sid)


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
                 os.environ['PREFIX'] + ev['name'] + ' at ' + start_dt.astimezone(tz).strftime(date_fmt),
                 """
Don't forget!  There is an event coming up in %s days!

Event: %s
Time: from %s to %s
Location: %s
""" % (days_away, ev['name'], start_dt.astimezone(tz).strftime(date_fmt),
       isoparse(instance['attributes']['ends_at']).astimezone(tz).strftime(date_fmt),
       instance['attributes']['location']))

        sendsms(os.environ['TESTSMSTO'], os.environ['PREFIX'] + ev['name'] + ' at ' + start_dt.astimezone(tz).strftime(date_fmt))

# pprint(events)
