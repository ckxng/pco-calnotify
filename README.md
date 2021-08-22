# pco-calnotify
A calendar notifier for Planning Center Online

I had a need to notify a set group of people by text and/or email at regular intervals
prior to scheduled events (with a particular tag) in Planning Center Online.

This addresses two separate needs:

1. It is a method of contacting a single group of people by email and/or text, depending 
   on their specific personal preferences.
3. It allows event reminders to be sent automatically to that group of people.  Planning 
   Center does not have the capability natively.

## The Solution
This script runs from cron and polls Planning Center Online for future event instances 
match a certain tag.  Then, it uses two separate services (Twilio and SendGrid) to notify 
the members of my group about those events.  

## Environments
The core configuration of this app takes place in a `.env` file in the project root.  
Take a look at `.env.sample` for an annotated example.

The specific list of contacts and their preferred contact methods are configured in 
`contacts.yaml`.  See `contacts-sample.yaml` for an example.

## Development
To run this app locally, clone the repo and run the following:

    python3 -m venv venv

    source env/bin/activate #Linux and Mac
    venv\Scripts\activate.bat #Windows

    pip install -r requirements.txt

    python3 app.py

When iterating over the codebase, you can set `TESTMODE=1` in `.env` to prevent
the API from actually sending texts and emails, saving your balance in Twilio for
real messages.
