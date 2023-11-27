from flask import Flask, render_template
import requests
from icalendar import Calendar
from datetime import datetime, timedelta
import pytz
from itertools import groupby

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
    #add 1 day to current date
    current_date = datetime.now(pytz.timezone('America/Sao_Paulo')).date() + timedelta(days=2)
    return [event for event in events if event['start'].date() <= current_date and event['end'].date() >= current_date]

@app.route('/')
def index():
    #creat a disctionary of events with name and url
    dic_events = {"Sala Multiuso II - 2E": "https://calendar.google.com/calendar/ical/unicamp.br_39uv0cjnnp55namoohfp5reh64%40group.calendar.google.com/public/basic.ics",
               "Sala Multiuso I - 1D": "https://calendar.google.com/calendar/ical/unicamp.br_db9jhcseff6a3shfhn9bpq8oa0%40group.calendar.google.com/public/basic.ics",
               "Sala Laboratório II - 1E": "https://calendar.google.com/calendar/ical/unicamp.br_un4jejd9b9u809p5lckfvknfp8%40group.calendar.google.com/public/basic.ics",
               "Sala Laboratório I - 1D": "https://calendar.google.com/calendar/ical/unicamp.br_prc9hoe8r6kvidn15prn7napao%40group.calendar.google.com/public/basic.ics",
               "Sala de Idiomas I - 2E": "https://calendar.google.com/calendar/ical/unicamp.br_rg8c8vr5ajf1p2rvd9hnihkg2g%40group.calendar.google.com/public/basic.ics",
               "Sala Auditório - 1E": "https://calendar.google.com/calendar/ical/unicamp.br_o4lfdobcojlmdcrgcp2kvpkm7c%40group.calendar.google.com/public/basic.ics"
    }
    #dic_events = {"Sala de Idiomas I - 2E": "https://calendar.google.com/calendar/ical/unicamp.br_rg8c8vr5ajf1p2rvd9hnihkg2g%40group.calendar.google.com/public/basic.ics"
    #              }

    all_events = []
    for location, ics_url in dic_events.items():
        ics_content = fetch_ics(ics_url)
        events = parse_ics(ics_content)
        current_events = filter_current_events(events)
        for event in current_events:
            event['location'] = location
            all_events.append(event)

    # Group events by location and sort by start time
    all_events.sort(key=lambda x: (x['location'], x['start']))
    events_by_location = {k: list(g) for k, g in groupby(all_events, key=lambda x: x['location'])}

    current_date = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime("%d/%m/%Y")
    return render_template('index.html', events_by_location=events_by_location, current_date=current_date)

if __name__ == '__main__':
    app.run(debug=True)
