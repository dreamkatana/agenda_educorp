from flask import Flask, render_template
import requests
from icalendar import Calendar
from datetime import datetime
import pytz

app = Flask(__name__)

def fetch_ics(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_ics(ics_content):
    calendar = Calendar.from_ical(ics_content)
    events = []
    sao_paulo_tz = pytz.timezone('America/Sao_Paulo')
    for component in calendar.walk('vevent'):
        dtstart = component.get('dtstart').dt
        dtend = component.get('dtend').dt

        # Convert to timezone-aware datetime objects if necessary
        if not isinstance(dtstart, datetime):
            dtstart = datetime.combine(dtstart, datetime.min.time(), sao_paulo_tz)
        if dtstart.tzinfo is None or dtstart.tzinfo.utcoffset(dtstart) is None:
            dtstart = sao_paulo_tz.localize(dtstart)
        
        if not isinstance(dtend, datetime):
            dtend = datetime.combine(dtend, datetime.min.time(), sao_paulo_tz)
        if dtend.tzinfo is None or dtend.tzinfo.utcoffset(dtend) is None:
            dtend = sao_paulo_tz.localize(dtend)

        events.append({
            'summary': str(component.get('summary')),
            'start': dtstart,
            'end': dtend
        })
    return events

def filter_current_events(events):
    current_date = datetime.now(pytz.timezone('America/Sao_Paulo')).date()
    return [event for event in events if event['start'].date() <= current_date and event['end'].date() >= current_date]

@app.route('/')
def index():
    ics_url = "https://calendar.google.com/calendar/ical/unicamp.br_39uv0cjnnp55namoohfp5reh64%40group.calendar.google.com/public/basic.ics"
    ics_content = fetch_ics(ics_url)
    events = parse_ics(ics_content)
    current_events = filter_current_events(events)
    return render_template('index.html', events=current_events)

if __name__ == '__main__':
    app.run(debug=True)
