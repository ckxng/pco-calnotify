"""
an email and SMS sending library for the pco-calnotify app
"""
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from twilio.rest import Client
import os


def sendmail(to, subject, text, sendgridapikey=os.environ['SENDGRIDAPIKEY']):
    """
    Send a plain text email
    If apikey is not provided, it will be fetched from os.environ['SENDGRIDAPIKEY']
    :param to: the email address to send to
    :param subject: the email subject
    :param text: the plain text message to send
    :param sendgridapikey: SendGrid API Key
    """
    message = Mail(
        from_email=os.environ['MAILFROM'],
        to_emails=to,
        subject=subject,
        plain_text_content=text)
    try:
        sg = SendGridAPIClient(sendgridapikey)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)


def sendsms(to, text,
            twiliosid=os.environ['TWILIOSID'],
            twiliotoken=os.environ['TWILIOTOKEN'],
            twilioservicesid=os.environ['TWILIOSERVICESID']):
    """
    Sends a SMS
    If twiliosid is not provided, it will be fetched from os.environ['TWILIOSID'].
    If twiliotoken is not provided, it will be fetched from os.environ['TWILIOTOKEN'].
    If twilioservicesid is not provided, it will be fetched from os.environ['TWILIOSERVICESID'].
    :param to: phone number in string format matching +15551234567
    :param text: the plain text message to send
    :param twiliosid: the Twilio SID
    :param twiliotoken: the Twilio Token
    :param twilioservicesid: the Twilio Messaging Service SID
    """
    client = Client(twiliosid, twiliotoken)

    message = client.messages.create(
        messaging_service_sid=twilioservicesid,
        body=text,
        to=to
    )

    print(message.sid)